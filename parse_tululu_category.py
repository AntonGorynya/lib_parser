from bs4 import BeautifulSoup
from main import check_for_redirect, SITE_URL, download_book
from urllib.parse import urljoin
import requests
import argparse
import json


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
    parser.add_argument('--start_page', help='start_page', default=1, type=int)
    parser.add_argument('--end_page', help='end_page', default=None, type=int)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    current_page = args.start_page

    soup = get_soup(current_page)
    last_page = int(soup.select('.npage')[-1]['href'].split('/')[2])

    if args.end_page and args.end_page <= last_page:
        last_page = args.end_page
    else:
        print(f'Change last page to {last_page}')

    with open('books.json', 'w', encoding='utf-8') as file:
        file.write('[\n')
    while current_page <= last_page:
        print('Page:', current_page)
        soup = get_soup(current_page)
        for book_path in soup.select('.bookimage a'):
            book_path = book_path['href']
            book_id = book_path.strip('/')[1:]
            book_url = urljoin(SITE_URL, book_path)
            downloaded_book = download_book(book_url)
            if downloaded_book:
                with open('books.json', 'a', encoding='utf-8') as file:
                    json.dump(downloaded_book, file, ensure_ascii=False, indent=4)
                    file.write(',\n')
        current_page += 1
    with open('books.json', 'a', encoding='utf-8') as file:
        file.write('\n]')
