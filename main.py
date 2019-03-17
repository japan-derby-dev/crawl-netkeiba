import requests
from bs4 import BeautifulSoup

url = 'https://db.netkeiba.com/horse/2013105880/'

html = requests.get(url)
soup = BeautifulSoup(html.content, 'html.parser')

print(soup)