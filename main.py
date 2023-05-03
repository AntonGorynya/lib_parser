from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
from requests.models import PreparedRequest
import requests
import os
import re
import sys
import argparse
import time

SITE_URL = 'https://tululu.org/'
SOURCE_TEXT_URL = 'https://tululu.org/txt.php'
BOOK_PAGE_URL = 'https://tululu.org/b{id}/'


class RedirectError(TypeError):
    pass


def download_txt(url, filename, path='books'):
    filename = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filename, 'wb') as file:
        file.write(response.content)


def download_image(url, path='images'):
    _, filename = os.path.split(url)
    os.makedirs(path, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    filename = os.path.join(path, filename)
    with open(filename, 'wb') as file:
        file.write(response.content)


def download_book(book_url, skip_imgs=False, skip_txt=False, dest_folder=None):
    if not dest_folder:
        dest_folder = os.getcwd()

    book_id = urlsplit(book_url).path.strip('/')[1:]
    print('downloading book', book_id)
    request = PreparedRequest()
    request.prepare_url(SOURCE_TEXT_URL, {'id': book_id})
    text_url = request.url
    response = requests.get(book_url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    parsed_book = parse_book_page(soup, book_id)
    if not skip_txt:
        download_txt(text_url, parsed_book['title'], path=dest_folder)
    if not skip_imgs:
        download_image(parsed_book['img'], path=dest_folder)
    return parsed_book


def check_for_redirect(response):
    if response.is_redirect:
        raise RedirectError


def serialize_name(book_name):
    return re.sub(r'[^\w\. ]+', '', book_name)


def parse_book_page(soup, book_id):
    book_title, author = [
        serialize_name(x.strip()) for x in soup.select_one('#content > h1').text.split('::')
    ]
    book_title = f'{book_id}. {book_title}.txt'
    book_img = soup.select_one('.bookimage  a > img')['src']
    book_img = urljoin(BOOK_PAGE_URL.format(id=book_id), book_img)
    book_description = soup.select('#content table.d_book')[1].text
    book_comments = soup.select('.texts span')
    book_comments = [comment.text for comment in book_comments]
    book_genre = soup.select_one('span.d_book a').text
    return {
        'author': author,
        'title': book_title,
        'img': book_img,
        'description': book_description,
        'comments': book_comments,
        'genre': book_genre,
    }


def create_parser():
    parser = argparse.ArgumentParser(
        description='download books '
    )
    parser.add_argument('--start_id', help='First book ID', default=1, type=int)
    parser.add_argument('--end_id', help='Last book ID-1', default=11, type=int)
    parser.add_argument('--skip_imgs', help='Skip images downloading', default=False, action='store_true')
    parser.add_argument('--skip_txt', help='Skip book text downloading', default=False, action='store_true')
    parser.add_argument('--dest_folder', help='Destination folder', default=None)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    if args.dest_folder:
        os.makedirs(args.dest_folder, exist_ok=True)

    for book_id in range(args.start_id, args.end_id, 1):
        book_url = BOOK_PAGE_URL.format(id=book_id)
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
