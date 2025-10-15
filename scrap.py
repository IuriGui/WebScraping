import re
import time
import random
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import csv
from bs4 import BeautifulSoup

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
        print(e)
        print("Erro na url")
    except Exception as e:
        print(e)
    return None


def get_categories(url):
    """Acessa a lista de categorias e retorna os links delas"""

    bs = get_bs(url)

    #print("Visitando: "+url)

    try:

        categories_list = bs.find("ul", {"class": "nav nav-list"})

        if not categories_list:
            print("Não foi possível encontrar a lista de categorias")
            return None

        categories_list = categories_list.find("ul").find_all("li")

        if not categories_list:
            print("Não foi possível acessar a lista de categorias")

        all_links = []
        for category in categories_list:
            link_tag = category.find("a")
            # if not link_tag:
            #     continue
            href = link_tag.get("href")
            # if not href:
            #     continue
            all_links.append(URL_BASE + href)



        sample_size = min(5, len(all_links))
        random_links = random.sample(all_links, sample_size)


        categories_link_list = set(random_links)


        return categories_link_list

    except AttributeError as e:
        print("Tag não encontrada")
        print(e)
        return None
    except Exception as e:
        print(e)
        return None


def get_books(url, list_of_books_links=None):
    """Retorna todos os livros de uma página de categoria"""
    if url is None:
        return list_of_books_links

    print("Extraindo livros da url: " + url)

    if list_of_books_links is None:
        list_of_books_links = set()

    bs = get_bs(url)
    if bs is None:
        return list_of_books_links

    try:
        #print("Visitando: "+url )
        books_section = bs.find("section")

        list_of_books = books_section.find("ol").find_all("li")
        for book in list_of_books:
            link_tag = book.find("a")
            if not link_tag:
                #print("Tag <a> não encontrada")
                continue
            href = link_tag.get("href")
            if not href:
                #print("Href não encontrado")
                continue

            href = href.replace("../../..", "")
            list_of_books_links.add(URL_BASE + "catalogue" + href)

        link_next_page = bs.find("li", class_="next")
        if link_next_page:
            link_next_page = link_next_page.find("a").get("href")
            if link_next_page:
                new_url = re.sub(r'[^/]+$', link_next_page, url)
                # print(link_next_page)
                get_books(new_url, list_of_books_links)




        return list_of_books_links

    except AttributeError as e:
        print(e)
        return list_of_books_links

def clean_price(string, regex_price, regex_dot):

    clean = regex_price.sub("", string)
    clean = regex_dot.sub(',', clean)

    return clean

def scrapBookPage(url):
    regex_number = re.compile(r'\((\d+)\s+available\)')
    regex_price = re.compile(r'[^0-9.]')
    regex_dot = re.compile(r'\.')

    print("Extraindo dados do livro: " + url)

    try:
        bs = get_bs(url)

        ##title
        title_text = bs.find("h1").text
        title =  title_text if title_text else None

        ##price
        price_tag = bs.find("p", class_="price_color")
        price = clean_price(price_tag.text, regex_price, regex_dot) if price_tag else None

        ##Category
        category = None
        breadcrumb = bs.find("ul", class_="breadcrumb")
        if breadcrumb:
            active_li = breadcrumb.find("li", class_="active")
            if active_li:
                previous_li = active_li.find_previous_sibling("li")
                category = previous_li.get_text(strip = True) if previous_li else None

        #Rating
        p = bs.find("p", class_="star-rating")
        rating = p.get("class")[-1] if p else None

        ##Stock
        table = bs.find("table")
        stock = None
        if table:
            th = table.find("th", string="Availability")
            td =  th.find_next_sibling("td") if th else None
            if td:
                number = regex_number.search(td.text)
                stock = number.group(1) if number else None

        return {
            "title": title,
            "price": price,
            "category": category,
            "rating": rating,
            "stock": stock
        }



    except AttributeError as e:
        print(e)
        return None
    except Exception as e:
        print(e)

def createCSV(data_books):
    try:
        with open('catalogo_livros.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'price', 'category', 'rating', 'stock']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for book in data_books:
                writer.writerow(book)

        print("CSV criado com sucesso!")

    except IOError as e:
        print("Erro ao abrir/escrever o arquivo:", e)
    except Exception as e:
        print("Erro inesperado ao criar CSV:", e)


def main():
    #Pega categorias
    categories_link = get_categories(URL_BASE)

    book_links = set()
    #Itera sobre a lista de link categoria buscando links de livros
    for category in categories_link:
        get_books(category, book_links)

    ##Scrap books
    data_books = []
    for book in book_links:
        data_books.append(scrapBookPage(book))

    createCSV(data_books)

main()