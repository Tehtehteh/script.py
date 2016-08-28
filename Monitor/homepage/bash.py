from bs4 import BeautifulSoup as BS
import requests
import random

def rollPage():
    url = 'http://bash.im/index/'
    doc = requests.get(url=url).text
    soup = BS(doc, 'html.parser')
    url += str(random.randint(a=int(soup.find('input', {'class':'page'})['min']), b=int(soup.find('input', {'class':'page'})['max'])))
    return url

def getQuote(url):
    page = requests.get(url=url).text
    soup = BS(page, 'html.parser')
    quote = soup.find_all('div', {'class':'text'})[random.randint(1, 45)]
    return quote


def main():
    url = rollPage()
    quote = getQuote(url)
    return url, quote.getText(separator='\n')
