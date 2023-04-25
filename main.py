from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os
import re
import argparse

SITE = 'https://tululu.org/'
SOURCE_TEXT = 'https://tululu.org/txt.php?id={id}'
BOOK_PAGE = 'https://tululu.org/b{id}/'


def download_txt(url, filename, path='books'):
    filename = os.path.join(path, filename)
    os.makedirs(path, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(filename, 'wb') as file:
        file.write(response.content)

def download_image(url, path='books'):
    _, filename = os.path.split(url)
    os.makedirs(path, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if 'text/plain' not in response.headers['Content-Type']:
        raise requests.HTTPError


def serialize_name(book_name):
    return re.sub(r'[^\w\. ]+', '', book_name)


def parse_book_page(soup):
    book_title, author = [
        serialize_name(x.strip()) for x in soup.find("div", {"id": "content"}).find('h1').text.split('::')
    ]
    book_title = f'{i}. {book_title}.txt'
    book_img = soup.find('div', {'class': 'bookimage'}).find('a').find('img')['src']
    book_img = urljoin(SITE, book_img)
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
    parser.add_argument('--start_id', help='start_id', default=1)
    parser.add_argument('--end_id', help='end_id', default=11)
    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    for i in range(args.start_id, args.end_id, 1):
        text_url = SOURCE_TEXT.format(id=i)
        book_url = BOOK_PAGE.format(id=i)

        response = requests.get(book_url, allow_redirects=False)
        response.raise_for_status()
        if not response.is_redirect:
            soup = BeautifulSoup(response.text, 'lxml')
            serialize_book = parse_book_page(soup)
            try:
                download_txt(text_url, serialize_book['title'])
                download_image(serialize_book['img'])
            except requests.HTTPError:
                pass
