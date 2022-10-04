import os
from pathlib import Path

import requests

Path("./books").mkdir(parents=True, exist_ok=True)

for number in range(0, 10):
    url = f"https://tululu.org/txt.php?id=1{number}"
    response = requests.get(url)
    response.raise_for_status()

    filename = f'book{number}.txt'
    path_books = os.path.join(Path.cwd(), 'books')
    path_book = os.path.join(path_books, filename)

    with open(path_book, 'wb') as file:
        file.write(response.content)
