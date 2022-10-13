import os
import unicodedata

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from dotenv import load_dotenv


def download_txt(url, filename, folder='books/'):
    Path(folder).mkdir(parents=True, exist_ok=True)
    books_path = os.path.join(Path.cwd(), folder)

    response = requests.get(url)
    response.raise_for_status()

    if check_for_redirect(response) is True:
        book_path = os.path.join(books_path, f'{sanitize_filename(filename)}.txt')

        with open(book_path, 'wb') as file:
            file.write(response.content)

        return file


def download_image(url, image_name):
    Path('images/').mkdir(parents=True, exist_ok=True)
    books_path = os.path.join(Path.cwd(), 'images/')

    response = requests.get(url)
    response.raise_for_status()

    if check_for_redirect(response) is True:
        image_path = os.path.join(books_path, f'{image_name.strip()}.png')
        with open(image_path, 'wb') as file:
            file.write(response.content)


def check_for_redirect(response):
    if response.history is None:
        print('Connection error')
    else:
        return True


def parse_book_page(html_content, number_book):
    soup = BeautifulSoup(html_content, 'lxml')

    h1 = soup.find('h1')
    elements_title = h1.text.split('::')
    author, title = elements_title

    title_text = unicodedata.normalize("NFKD", title)
    author_text = unicodedata.normalize("NFKD", author)

    image_src = soup.find('div', class_='bookimage').find('a').find('img')['src']
    image_url = urljoin(f'https://tululu.org/b{number_book}', image_src)

    categories = soup.find('div', id='content').find('span', class_='d_book').find_all('a')
    categories_text = [category.get_text() for category in categories]

    comments = soup.find_all('div', class_='texts')
    comments_text = [comment.find('span', class_='black').get_text() for comment in comments]

    book = {
        'title': title_text,
        'author': author_text,
        'categories': categories_text,
        'comments': comments_text,
        'image_url': image_url
    }

    return book


if __name__ == '__main__':
    load_dotenv()

    Path("./books").mkdir(parents=True, exist_ok=True)

    try:
        for number in range(int(os.environ['BOOK_ID_START']), int(os.environ['BOOK_ID_END'])):

            params = {
                'id': number,
            }

            url_for_download = "https://tululu.org/txt.php"
            response = requests.get(url_for_download, params=params)
            response.raise_for_status()

            if check_for_redirect(response) is True and response.encoding == 'utf-8':
                url_for_parce = f"https://tululu.org/b{number}"
                response = requests.get(url_for_parce)

                if check_for_redirect(response) is True:
                    book = parse_book_page(response.text, number)
                    try:
                        download_image(book['image_url'], book['title'])
                        download_txt(url_for_download, book['title'])
                    except TypeError or IndexError as error:
                        print(error)

    except requests.exceptions.ConnectionError as error:
        print(error)
