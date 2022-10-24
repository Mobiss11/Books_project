import os
import time

import unicodedata
import argparse

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(books_info, folder='books/'):
    for book in books_info:

        Path(folder).mkdir(parents=True, exist_ok=True)
        books_path = os.path.join(Path.cwd(), folder)

        response = requests.get(book['book_url'])
        response.raise_for_status()
        check_for_redirect(response)

        filename = book['title']
        book_path = os.path.join(books_path, f'{sanitize_filename(filename)}.txt')

        with open(book_path, 'wb') as file:
            file.write(response.content)


def download_image(books_info):

    for book in books_info:
        image_name = book['title']
        image_url = book['image_url']
        Path('images/').mkdir(parents=True, exist_ok=True)
        books_path = os.path.join(Path.cwd(), 'images/')

        response = requests.get(image_url)
        response.raise_for_status()

        image_path = os.path.join(books_path, f'{image_name.strip()}.png')
        with open(image_path, 'wb') as file:
            file.write(response.content)


def parse_book_page(book_links):

    books = []

    for link in book_links:
        response = requests.get(link)
        response.raise_for_status()
        check_for_redirect(response)

        soup = BeautifulSoup(response.text, 'lxml')

        h1 = soup.find('h1')
        elements_title = h1.text.split('::')
        author, title = elements_title

        title_text = unicodedata.normalize("NFKD", title)
        author_text = unicodedata.normalize("NFKD", author)

        image_src = soup.find('div', class_='bookimage').find('a').find('img')['src']
        image_url = urljoin(f'{link}', image_src)

        categories = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
        categories_text = [category.get_text() for category in categories]

        comments = soup.find_all('div', class_='texts')
        comments_text = [comment.find('span', class_='black').get_text() for comment in comments]

        book = {
            'title': title_text,
            'author': author_text,
            'categories': categories_text,
            'comments': comments_text,
            'image_url': image_url,
            'book_url': link
        }

        books.append(book)

    return books


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.ConnectionError


def get_book_links(html_content):
    soup = BeautifulSoup(html_content, 'lxml')

    table_tags = soup.find('div', id='content').find_all('table', class_='d_book')
    a_tags = [a.find('a', href=True) for a in table_tags]
    hrefs = [href['href'] for href in a_tags]
    links = [urljoin('https://tululu.org/', href) for href in hrefs]

    return links


if __name__ == '__main__':

    for page_number in range(1, 5):
        url_for_parce = f"https://tululu.org/l55/"
        url_page = urljoin(url_for_parce, str(page_number))

        response = requests.get(url_page)
        response.raise_for_status()
        check_for_redirect(response)

        book_links = get_book_links(response.text)

        books_info = parse_book_page(book_links)

        download_image(books_info)
        download_txt(books_info)




