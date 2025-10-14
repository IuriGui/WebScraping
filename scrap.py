import re
import time
import random
from urllib.request import urlopen


from bs4 import BeautifulSoup
from urllib3.util import url




#time.sleep(random.uniform(2, 5))


def getCategoryLinks(url):
   html = urlopen(url)
   links = set()
   bs = BeautifulSoup(html.read(), 'html.parser')
   categorias = bs.find("ul", {"class": "nav nav-list"}).find_all("li")
   for categoria in categorias:
       link = categoria.find("a").get("href")
       links.add(url + link)


   return links


def getBookLinks(url):
   if(url == None):
       return None
   html = urlopen(url)


   html = urlopen(url)


   bs = BeautifulSoup(html.read(), 'html.parser')
   links = set()


   padrao = re.compile(r'/[A-Za-z0-9_-]+/index\.html')


   t = bs.find("ol")
   for li in t.find_all("li"):
       link = li.find("a").get("href")
       link = padrao.search(link)
       li = "https://books.toscrape.com/catalogue" + link.group()
       links.add(li)


   return links


def getBooksLinkInCategory(links_category):
headers = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    # Ou, para ser transparente:
  # 'User-Agent': 'Projeto Academico de Web Scraping para a disciplina de Análise de Dados e Extração de Conhecimento - Universidade Federal de Santa maria - Contato: seu.email@dominio.com'
}
##<ul class="nav nav-list"> lista de categorias


#link_categorias = getCategoryLinks("https://books.toscrape.com/")

links_categorias = getCategoryLinks("https://books.toscrape.com/")
links_books = getBookLinks("https://books.toscrape.com/")
for link in links_books:
   print(link)
