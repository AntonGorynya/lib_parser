from bs4 import BeautifulSoup
import requests
import os
import re

SOURCE_TEXT = 'https://tululu.org/txt.php?id={id}'
BOOK_PAGE = 'https://tululu.org/b{id}/'

def download_file(url, path):
    folder, file_name = os.path.split(path)
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url, allow_redirects=False)
    response.raise_for_status()
    check_for_redirect(response)
    with open(path, 'wb') as file:
        file.write(response.content)

def check_for_redirect(response):
    if 'text/plain' not in response.headers['Content-Type']:
        raise requests.HTTPError

def check_book_name(book_name):
    return re.sub(r'[^\w\.]+',' ', book_name)



if __name__ == '__main__':
    print(check_book_name('dfddf.txt'))

    # for i in range(10, 11, 1):
    #     text_url = SOURCE_TEXT.format(id=i)
    #     book_url = BOOK_PAGE.format(id=i)
    #
    #     response = requests.get(book_url, allow_redirects=False)
    #     response.raise_for_status()
    #     if not response.is_redirect:
    #         soup = BeautifulSoup(response.text, 'lxml')
    #         book_title, author = [x.strip() for x in soup.find("div", {"id": "content"}).find('h1').text.split('::')]
    #         book_img = soup.find("div", {"class": "bookimage"}).find('a').find('img')['src']
    #         book_description = soup.find("div", {"id": "content"}).find_all('table')[2].text


        # try:
        #     download_file(text_url, book_title)
        # except requests.HTTPError:
        #     pass