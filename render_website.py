import argparse
import json

from pathlib import Path

from environs import Env
from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape


def fetch_books_data(path_of_books_data_file):
    with path_of_books_data_file.open('r', encoding='utf-8') as books_data_file:
        books_data = json.load(books_data_file)

    return books_data


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

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        books_data=books_data
    )

    with open('index.html', 'w', encoding="utf-8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()


if __name__ == '__main__':
    main()