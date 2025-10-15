import re
import time
import random
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import urlopen


from bs4 import BeautifulSoup
from urllib3.util import url


URL_BASE = "https://books.toscrape.com/"



def get_bs(url):
    """Acessa a url, retorna o objeto beatifulSoup e agurda o tempinho pela educação"""
    try:
        html = urlopen(url)
        bs_obj = BeautifulSoup(html, "html.parser")
        #time.sleep(random.uniform(2, 5))
        return bs_obj
    except HTTPError as e:
        print(e)
    except URLError as e:
        print("Erro na url")
    return None


def get_categories(url):
    """Acessa a lista de categorias e retorna os links delas"""

    bs = get_bs(url)

    ##Lista de retorno
    categories_link_list = set()

    try:

        categories_list = bs.find("ul", {"class": "nav nav-list"})

        if not categories_list:
            print("Não foi possível encontrar a lista de categorias")
            return None

        categories_list = categories_list.find("ul").find_all("li")

        if not categories_list:
            print("Não foi possível acessar a lista de categorias")


        for category in categories_list:
            link_tag = category.find("a")
            if not link_tag:
                continue
            href = link_tag.get("href")
            if not href:
                continue
            categories_link_list.add(URL_BASE + href)

        return categories_link_list

    except AttributeError as e:
        print("Tag não encontrada")
        return None
    except Exception as e:
        print(e)
        return None


def get_books(url, list_of_books_links=None):
    """Retorna todos os livros de uma página de categoria"""

    if url is None:
        return list_of_books_links

    if list_of_books_links is None:
        list_of_books_links = set()

    bs = get_bs(url)

    try:
        print("Pegando livros...   " )
        books_section = bs.find("section")
        if not books_section:
            print("Não foi possível encortrar a seção de livros")
            return None

        list_of_books = books_section.find("ol").find_all("li")
        if not list_of_books:
            print("Não foi possível acessar a lista de livros")
            return None

        for book in list_of_books:
            link_tag = book.find("a")
            if not link_tag:
                print("Tag <a> não encontrada")
                continue
            href = link_tag.get("href")
            if not href:
                print("Href não encontrado")
                continue
            href = href.replace("../../..", "")
            list_of_books_links.add(URL_BASE + "catalogue" + href)

        link_next_page = bs.find("li", class_="next")
        if not link_next_page:
            print("Esta categoria não possui mais páginas")
            return None

        link_next_page = link_next_page.find("a").get("href")

        if link_next_page:
            new_url = re.sub(r'[^/]+$', link_next_page, url)
            #print(link_next_page)
            get_books(new_url, list_of_books_links)

        return list_of_books_links

    except AttributeError as e:
        print(e)
        return None



def main():
    categories_link = get_categories(URL_BASE)



fd = "https://books.toscrape.com/catalogue/wall-and-piece_971/index.html"

ls = get_bs(fd)

