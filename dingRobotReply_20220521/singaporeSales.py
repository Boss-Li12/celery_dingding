import requests
from bs4 import BeautifulSoup

def get_sinapore_sales():
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    res = requests.get('https://www.usd-cny.com/icbc.htm', headers = headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    time = soup.select('body > section > div > div > article > p')[0].text[21:]
    #print(time)
    price = soup.select('body > section > div > div > article > table > tr:nth-child(6) > td:nth-child(2)')[0].text
    #print(price)
    return time, price



#get_sinapore_sales()
#body > section > div > div > article > table > tbody > tr:nth-child(6) > td:nth-child(2)
#body > section > div > div > article > p