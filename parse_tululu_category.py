from bs4 import BeautifulSoup
from main import check_for_redirect, SITE_URL, download_book, RedirectError
from urllib.parse import urljoin
import time
import requests
import sys

FANTSTIC_BOOK_URL = 'https://tululu.org/l55/{page}'


if __name__ == '__main__':
    current_page = 1
    last_page = 10
    while current_page <= last_page:
        print('Page:', current_page)
        response = requests.get(FANTSTIC_BOOK_URL.format(page=current_page))
        response.raise_for_status()
        check_for_redirect(response)
        soup = BeautifulSoup(response.text, 'lxml')
        book_soup = soup.find_all("table", {"class": "d_book"})
        #last_page = int(soup.find_all('a', {'class': 'npage'})[-1]['href'].split('/')[2])
        for i, book in enumerate(book_soup):
            book_path = book.find('a')['href']
            book_id = book_path.strip('/')[1:]
            book_url = urljoin(SITE_URL, book_path)
            downloaded_book = download_book(book_url)
        current_page += 1


