import csv
from dataclasses import dataclass, fields, astuple
from typing import List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


QUOTE_FIELDS = [field.name for field in fields(Quote)]


def parse_single_quote(quote: BeautifulSoup) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tags > .tag")]
    )


def get_single_page(page: BeautifulSoup) -> List[Quote]:
    quotes = page.select(".quote")
    return [parse_single_quote(quote) for quote in quotes]


def get_quotes() -> List[Quote]:
    base_page = requests.get(BASE_URL).content
    first_page = BeautifulSoup(base_page, "html.parser")
    all_pages = get_single_page(first_page)
    next_page = first_page.select_one(".next > a")

    while next_page:
        new_url = urljoin(BASE_URL, next_page["href"])
        page_content = requests.get(new_url).content
        parsed_page = BeautifulSoup(page_content, "html.parser")
        all_pages.extend(get_single_page(parsed_page))
        next_page = parsed_page.select_one(".next > a")

    return all_pages


def write_products_to_csv(path: str, quotes: list[Quote]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(QUOTE_FIELDS)
        writer.writerows([astuple(quote) for quote in quotes])


def main(output_csv_path: str) -> None:
    quotes = get_quotes()
    write_products_to_csv(output_csv_path, quotes)


if __name__ == "__main__":
    main("quotes.csv")
