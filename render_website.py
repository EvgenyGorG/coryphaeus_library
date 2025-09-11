import argparse
import json

from pathlib import Path

from environs import Env
from livereload import Server
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


def fetch_books_data(path_of_books_data_file):
    with path_of_books_data_file.open('r', encoding='utf-8') as books_data_file:
        books_data = json.load(books_data_file)

    return books_data


def chunk_books_data(books_data):
    return list(chunked(books_data, 2))


def on_reload(chunked_books_data):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        chunked_books_data=chunked_books_data
    )

    with open('index.html', 'w', encoding="utf-8") as file:
        file.write(rendered_page)


def main():
    env = Env()
    env.read_env()

    path_of_books_data_file = env.str(
        'BOOKS_DATA_FILE_PATH', default='meta_data.json'
    )

    parser = argparse.ArgumentParser(
        description='Отрисовка библиотеки "Корифей"')
    parser.add_argument(
        '-p',
        '--books_data_path',
        default=path_of_books_data_file,
        type=Path,
        help='Относительный путь к файлу с данными книг'
    )
    args = parser.parse_args()

    path_of_books_data_file = args.books_data_path

    if path_of_books_data_file.exists():
        books_data = fetch_books_data(path_of_books_data_file)
    else:
        raise FileNotFoundError('Файл не найден, проверьте наличие файла по заданному пути.')

    chunked_books_data = chunk_books_data(books_data)

    on_reload(chunked_books_data)

    server = Server()
    server.watch('template.html', lambda: on_reload(chunked_books_data))
    server.serve(root='.')


if __name__ == '__main__':
    main()