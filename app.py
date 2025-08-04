from flask import Flask, render_template  #create server
import requests
from bs4 import BeautifulSoup  #web scraping
import pandas as pd #data manipulation

app = Flask(__name__)


@app.route('/')

def scraping_books():
    url="https://books.toscrape.com/"
    response=requests.get(url)
    soup=BeautifulSoup(response.text,'html.parser')
    books=soup.find_all('li',class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    book_data = []
    for book in books:
        name = book.find('h3').find("a")
        price = books.find("p",class_="")

        name = name.get('title')if name else None
        price = price.get('price')if price else None

        book_data.append([name],[price])
    df = pd.DataFrame(book_data, columns=['Name', 'Price'])
    return render_template('index.html', tables=df.to_html(index=False,classes="table table-striped"))

#def index():
#    return render_template('home.html')

#if __name__ == '__main__':
#    app.run(debug=True,port=3000)