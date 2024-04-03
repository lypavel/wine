from datetime import datetime
from collections import defaultdict
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from environs import Env
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pandas import read_excel


def calculate_shop_age() -> int:
    foundation_year = 1920
    return datetime.today().year - foundation_year


def get_age_pronunciation(age: int) -> str:
    if age % 100 in range(11, 15):
        return "лет"
    elif age % 10 == 1:
        return "год"
    elif age % 10 in range(2, 5):
        return "года"
    return "лет"


def load_wines_from_xlsx(file_path: Path) -> dict:
    return read_excel(
        file_path
    ).fillna('').to_dict(orient='records')


def group_drinks_by_category(drinks: list) -> defaultdict:
    drink_categories = defaultdict(list)
    for wine in drinks:
        drink_categories[wine['Категория']].append(wine)

    return drink_categories


if __name__ == "__main__":
    env_variables = Env()
    env_variables.read_env()
    DRINKS_FILE_PATH = Path(env_variables.str('XLSX_FILE'))

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    drinks = load_wines_from_xlsx(DRINKS_FILE_PATH)
    drink_categories = group_drinks_by_category(drinks)
    shop_age = calculate_shop_age()

    rendered_page = template.render(
        shop_age=f"{shop_age} {get_age_pronunciation(shop_age)}",
        drink_categories=drink_categories
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()
