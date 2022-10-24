import os
import time

import unicodedata
import argparse

from pathlib import Path
from urllib.parse import urljoin

import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.ConnectionError


def get_book_links(html_content):
    soup = BeautifulSoup(html_content, 'lxml')

    table_tags = soup.find('div', id='content').find_all('table', class_='d_book')
    a_tags = [a.find('a', href=True) for a in table_tags]
    hrefs = [href['href'] for href in a_tags]
    links = [urljoin('https://tululu.org/', href) for href in hrefs]
    print(len(links))

    return links


if __name__ == '__main__':
    url_for_parce = f"https://tululu.org/fantastic/"
    response = requests.get(url_for_parce)
    response.raise_for_status()
    check_for_redirect(response)

    get_book_links(response.text)