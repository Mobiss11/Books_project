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

    file = sanitize_filename(filename)

    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 301:
        book_path = os.path.join(books_path, f'{file}.txt')

        with open(book_path, 'wb') as file:
            file.write(response.content)

        return file


def download_image(url, image_name):
    Path('images/').mkdir(parents=True, exist_ok=True)
    books_path = os.path.join(Path.cwd(), 'images/')

    response = requests.get(url)
    response.raise_for_status()

    if response.status_code != 301:
        with open(f'{books_path}{image_name.strip()}.png', 'wb') as file:
            file.write(response.content)


def check_for_redirect(response):
    try:
        print(response.status_code)
        if response.status_code == 200 and response.encoding == 'utf-8':
            return True
    except requests.exceptions.ConnectionError:
        raise requests.exceptions.ConnectionError('Connection error')


def parse_book_page(html_content):
    soup = BeautifulSoup(html_content, 'lxml')

    h1 = soup.find('h1')
    elements_title = h1.text.split('::')
    author, title = elements_title[1], elements_title[0]

    title_text = unicodedata.normalize("NFKD", title)
    author_text = unicodedata.normalize("NFKD", author)

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


def main(start_id, end_id):
    Path("./books").mkdir(parents=True, exist_ok=True)

    for number in range(start_id, end_id):

        params = {
            'id': number,
        }

        url_for_download = "https://tululu.org/txt.php"
        response = requests.get(url_for_download, params=params)
        response.raise_for_status()

        if check_for_redirect(response) is True:
            url_for_parce = f"https://tululu.org/b{number}"
            response = requests.get(url_for_parce)

            if response.status_code != 301:
                book = parse_book_page(response.text)
                try:
                    download_image(book['image_url'], book['title'])
                    download_txt(url_for_download, book['title'])
                except TypeError or IndexError as error:
                    print(error)


if __name__ == '__main__':
    load_dotenv()
    main(int(os.environ['BOOK_ID_START']), int(os.environ['BOOK_ID_END']))
