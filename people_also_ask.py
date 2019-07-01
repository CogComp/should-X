import requests
from bs4 import BeautifulSoup
import html2text
import urllib.request

def example():
    link = "https://www.google.com/search?client=firefox-b-d&source=hp&ei=v0mUXPu2ApTljwS6iLnABA&ei=lAyVXMPFCsaUsgXqmZT4DQ&q=what+is+java"

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    page = requests.get(link ,headers = headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    #For answers :
    mydivs = soup.find_all('div', class_="ILfuVd NA6bn")

if __name__ == "__main__":
    example()
