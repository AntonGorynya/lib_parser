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


def download_book(book_url):
    try:
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
        download_txt(text_url, parsed_book['title'])
        download_image(parsed_book['img'])
        return parsed_book
    except requests.HTTPError as error:
        print(error, file=sys.stderr)
    except requests.exceptions.ConnectionError as error:
        print(error, file=sys.stderr)
        print('Trying to reconnect over 5 seconds...')
        time.sleep(10)
    except RedirectError as error:
        print(f'Redirect error. Book with id {book_id} does not exist', file=sys.stderr)


def check_for_redirect(response):
    if response.is_redirect:
        raise RedirectError


def serialize_name(book_name):
    return re.sub(r'[^\w\. ]+', '', book_name)


def parse_book_page(soup, book_id):
    book_title, author = [
        serialize_name(x.strip()) for x in soup.find("div", {"id": "content"}).find('h1').text.split('::')
    ]
    book_title = f'{book_id}. {book_title}.txt'
    book_img = soup.find('div', {'class': 'bookimage'}).find('a').find('img')['src']
    book_img = urljoin(BOOK_PAGE_URL.format(id=book_id), book_img)
    book_description = soup.find('div', {'id': 'content'}).find_all('table')[2].text
    book_comments = soup.find_all('div', {'class': 'texts'})
    book_genre = soup.find('span', {'class': 'd_book'}).find('a').text
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
    parser.add_argument('--start_id', help='start_id', default=1, type=int)
    parser.add_argument('--end_id', help='end_id', default=11, type=int)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id, 1):
        book_url = BOOK_PAGE_URL.format(id=book_id)
        download_book(book_url)

