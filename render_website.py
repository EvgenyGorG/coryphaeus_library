import argparse
import json

from pathlib import Path

from environs import Env
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


BOOKS_IN_ROW = 2


def fetch_books_data(path_of_books_data_file):
    with path_of_books_data_file.open('r', encoding='utf-8') as books_data_file:
        books_data = json.load(books_data_file)

    return books_data


def chunk_books_data(books_data, portion):
    return list(chunked(books_data, portion))


def on_reload(chunked_books):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    for number, books in enumerate(chunked_books, 1):
        chunked_books_data = chunk_books_data(books, BOOKS_IN_ROW)

        rendered_page = template.render(
            chunked_books_data=chunked_books_data,
            number_of_pages=len(chunked_books),
            current_page=number
        )

        Path('pages').mkdir(parents=True, exist_ok=True)

        with open(f'pages/index{number}.html', 'w', encoding='utf-8') as file:
            file.write(rendered_page)


def main():
    env = Env()
    env.read_env()

    path_of_books_data_file = env.str(
        'BOOKS_DATA_FILE_PATH', default='meta_data.json'
    )

    books_in_page = env.int('BOOKS_IN_PAGE', default=10)

    parser = argparse.ArgumentParser(
        description='Отрисовка библиотеки "Корифей"')
    parser.add_argument(
        '-p',
        '--books_data_path',
        default=path_of_books_data_file,
        type=Path,
        help='Относительный путь к файлу с данными книг'
    )
    parser.add_argument(
        '-nb',
        '--books_in_page',
        default=books_in_page,
        type=int,
        help='Количество книг на странице'
    )
    args = parser.parse_args()

    path_of_books_data_file = args.books_data_path
    books_in_page = args.books_in_page

    if path_of_books_data_file.exists():
        books_data = fetch_books_data(path_of_books_data_file)
    else:
        raise FileNotFoundError('Файл не найден, проверьте наличие файла по заданному пути.')

    chunked_books = chunk_books_data(books_data, books_in_page)

    on_reload(chunked_books)

    server = Server()
    server.watch('template.html', lambda: on_reload(chunked_books))
    server.serve(root='.')


if __name__ == '__main__':
    main()