import os
import time

import unicodedata
import argparse

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def download_txt(book_info, folder):
    Path(folder).mkdir(parents=True, exist_ok=True)
    books_path = os.path.join(Path.cwd(), folder)

    response = requests.get(book_info['book_url'])
    response.raise_for_status()
    check_for_redirect(response)

    filename = book_info['title']
    book_path = os.path.join(books_path, f'{sanitize_filename(filename)}.txt')

    with open(book_path, 'wb') as file:
        file.write(response.content)


def download_image(book_info, folder):
    image_name = book_info['title']
    image_url = book_info['image_url']
    Path('images/').mkdir(parents=True, exist_ok=True)
    books_path = os.path.join(Path.cwd(), folder)

    response = requests.get(image_url)
    response.raise_for_status()

    image_path = os.path.join(books_path, f'{image_name.strip()}.png')
    with open(image_path, 'wb') as file:
        file.write(response.content)


def parse_book_page(book_link):
    response = requests.get(book_link)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')

    h1 = soup.find('h1')
    elements_title = h1.text.split('::')
    author, title = elements_title

    title_text = unicodedata.normalize("NFKD", title)
    author_text = unicodedata.normalize("NFKD", author)

    image_src = soup.find('div', class_='bookimage').find('a').find('img')['src']
    image_url = urljoin(f'{book_link}', image_src)

    categories = soup.select('.d_book a')
    categories_text = [category.get_text() for category in categories]

    comments = soup.select('.texts')
    comments_text = [comment.find('span', class_='black').get_text() for comment in comments]

    book = {
        'title': title_text,
        'author': author_text,
        'categories': categories_text,
        'comments': comments_text,
        'image_url': image_url,
        'book_url': book_link
    }

    return book


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.ConnectionError


def get_book_links(html_content):
    soup = BeautifulSoup(html_content, 'lxml')

    tag_a = soup.select(".d_book a")

    hrefs = [href.get('href') for href in tag_a]
    books_href = []

    for href in hrefs:
        if href.find('b') != -1:
            books_href.append(href)

    links = [urljoin('https://tululu.org/', href) for href in books_href]

    return links


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Программа парсит и скачивает книги'
    )
    parser.add_argument('--start_page', help='Начальная страница', type=int, default=1)
    parser.add_argument('--end_page', help='Последняя страница', type=int, default=1)
    parser.add_argument('--path_txt_info', help='Путь для скачивания текстовой информации', type=str, default='books/')
    parser.add_argument('--path_images', help='Путь для скачивания фото', type=str, default='images/')
    parser.add_argument('--skip_imgs', help='Параметр для пропуска скачивания книг', action='store_true')
    parser.add_argument('--skip_txt', help='Параметр для пропуска скачивания текста', action='store_true')
    args = parser.parse_args()

    for page_number in range(args.start_page, args.end_page):
        try:
            url_for_parce = f"https://tululu.org/l55/"
            url_page = urljoin(url_for_parce, str(page_number))

            response = requests.get(url_page)
            response.raise_for_status()
            check_for_redirect(response)

            book_links = get_book_links(response.text)

            books = [parse_book_page(book) for book in book_links]

            if args.skip_txt is not True:
                for book in books:
                    download_txt(book, args.path_txt_info)

            if args.skip_imgs is not True:
                for book in books:
                    download_image(book, args.path_images)

        except requests.exceptions.HTTPError and requests.exceptions.ConnectionError as error:
            print(error)
            time.sleep(10)
