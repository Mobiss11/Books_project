import os
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


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


def check_for_redirect(response):
    if response.encoding == 'utf-8':
        return True
    else:
        return False


def main():
    Path("./books").mkdir(parents=True, exist_ok=True)

    for number in range(0, 10):
        url = f"https://tululu.org/txt.php?id=1{number}"
        response = requests.get(url)
        response.raise_for_status()

        if check_for_redirect(response) is True:

            url = f"https://tululu.org/b{number}"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, 'lxml')

            h1 = soup.find('h1')
            title = h1.text.split('::')
            clean_title = unicodedata.normalize("NFKD", title[0])

            download_txt(url, clean_title)

        else:
            path_books = os.path.join(Path.cwd(), "books")

            url = f"https://tululu.org/"
            response = requests.get(url)
            response.raise_for_status()

            filename = f'main_url{number}.txt'
            path_book = os.path.join(path_books, filename)

            with open(path_book, 'wb') as file:
                file.write(response.content)


if __name__ == '__main__':
    main()
