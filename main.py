import os
import unicodedata

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from config import book_start_id, book_end_id


def download_txt(url, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    path_books = os.path.join(Path.cwd(), folder)

    file = sanitize_filename(filename)

    response = requests.get(url)
    response.raise_for_status()

    path_book = os.path.join(path_books, f'{file}.txt')

    with open(path_book, 'wb') as file:
        file.write(response.content)

    return file


def download_image(url, image_name):
    Path('images/').mkdir(parents=True, exist_ok=True)
    path_books = os.path.join(Path.cwd(), 'images/')

    response = requests.get(url)
    response.raise_for_status()

    with open(f'{path_books}{image_name.strip()}.png', 'wb') as file:
        file.write(response.content)


def check_for_redirect(response):
    if response.encoding == 'utf-8':
        return True
    else:
        return False


def parse_book_page(html_content):
    try:

        soup = BeautifulSoup(html_content, 'lxml')

        h1 = soup.find('h1')
        title = h1.text.split('::')
        title_text = unicodedata.normalize("NFKD", title[0])
        author_text = unicodedata.normalize("NFKD", title[1])

        image_src = soup.find('div', class_='bookimage').find('a').find('img')['src']
        image_url = urljoin('https://tululu.org', image_src)

        categories = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
        categories_text = []
        for category in categories:
            categories_text.append(category.get_text())

        comments = soup.find_all('div', class_='texts')
        comments_text = []
        for comment in comments:
            comment_text = comment.find('span', class_='black')
            comments_text.append(comment_text.get_text())

        book = {
            'title': title_text,
            'author': author_text,
            'categories': categories_text,
            'comments': comments_text,
            'image_url': image_url
        }

        return book

    except IndexError as error:
        print(error)


def main(start_id, end_id):
    Path("./books").mkdir(parents=True, exist_ok=True)

    for number in range(start_id, end_id):

        params = {
            'id': number,
        }

        url = "https://tululu.org/txt.php"
        response = requests.get(url, params=params)
        response.raise_for_status()

        if check_for_redirect(response) is True:
            url = f"https://tululu.org/b{number}"
            response = requests.get(url)
            book_info = parse_book_page(response.text)

            try:
                download_image(book_info['image_url'], book_info['title'])
                download_txt(url, book_info['title'])
            except TypeError as error:
                print(error)


if __name__ == '__main__':
    main(book_start_id, book_end_id)
