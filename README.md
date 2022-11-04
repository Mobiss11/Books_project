# Books_project

Программа, которая парсит книги с сайта.

## Запуск 
1. Установить зависимости из файла `requirements.txt`.
```
pip install -r requirements.txt.
```
## Запуск модуля main.py
1. Запустить скрипт компандой, первый аргумент - id первой книги, второй аргумент - id последней книги.
```
python main.py 1 10
```

## Запуск модуля parse_tululu_category.py
1. Запустить скрипт компандой. У модуля есть опциональные аргументы
- `--start_page` - Начальная страница, значение по умолчанию `1`
- `--end_page` - Последняя страница, значение по умолчанию `1`
- `--path_txt_info` - Путь для скачивания текстовой информации, значение по умолчанию `books/`
- `--path_images` - Путь для скачивания фото, значение по умолчанию `images/`
- `--skip_imgs` - Параметр для пропуска скачивания книг, значение по умолчанию `no skip`
- `--skip_txt` - Параметр для пропуска скачивания текста, значение по умолчанию `no skip`
```
python parse_tululu_category.py --start_page 1 --end_page 3 

```


