from bs4 import BeautifulSoup
from main import check_for_redirect, SITE_URL, download_book, RedirectError
from urllib.parse import urljoin
import sys
import time
import requests
import argparse
import json
import os


FANTSTIC_BOOK_URL = 'https://tululu.org/l55/{page}'


def get_soup(page_number):
    response = requests.get(FANTSTIC_BOOK_URL.format(page=page_number))
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


def create_parser():
    parser = argparse.ArgumentParser(
        description='download fantastic books '
    )
    parser.add_argument('--start_page', help='start page number. Default value: 1', default=1, type=int)
    parser.add_argument('--end_page', help='end page number. Default value: None ', default=None, type=int)
    parser.add_argument('--skip_imgs', help='Skip images downloading', default=False, action='store_true')
    parser.add_argument('--skip_txt', help='Skip book text downloading', default=False, action='store_true')
    parser.add_argument('--json_path', help='Path to json file', default='books.json')
    parser.add_argument('--dest_folder', help='Destination folder', default=None)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    current_page = args.start_page

    soup = get_soup(current_page)
    last_page = int(soup.select('.npage')[-1]['href'].split('/')[2])

    if args.dest_folder:
        os.makedirs(args.dest_folder, exist_ok=True)
    if args.json_path:
        path, _ = os.path.split(args.json_path)
        if path:
            os.makedirs(path, exist_ok=True)
    if args.end_page and args.end_page <= last_page:
        last_page = args.end_page
    else:
        print(f'Change last page to {last_page}')

    with open(args.json_path, 'w', encoding='utf-8') as file:
        file.write('[\n')
    while current_page <= last_page:
        print('Page:', current_page)
        soup = get_soup(current_page)
        for book_path in soup.select('.bookimage a'):
            book_path = book_path['href']
            book_id = book_path.strip('/')[1:]
            book_url = urljoin(SITE_URL, book_path)
            try:
                downloaded_book = download_book(
                    book_url,
                    skip_imgs=args.skip_imgs,
                    skip_txt=args.skip_txt,
                    dest_folder=args.dest_folder
                )
            except requests.HTTPError as error:
                print(error, file=sys.stderr)
            except requests.exceptions.ConnectionError as error:
                print(error, file=sys.stderr)
                print('Trying to reconnect over 5 seconds...')
                time.sleep(10)
            except RedirectError as error:
                print(f'Redirect error. Book with id {book_id} does not exist', file=sys.stderr)
            if downloaded_book:
                with open(args.json_path, 'a', encoding='utf-8') as file:
                    json.dump(downloaded_book, file, ensure_ascii=False, indent=4)
                    file.write(',\n')
        current_page += 1
    with open(args.json_path, 'a', encoding='utf-8') as file:
        file.write('\n]')
