# from flask import Flask, render_template  #create server
# import requests
# from bs4 import BeautifulSoup  #web scraping
# import pandas as pd #data manipulation

# app = Flask(__name__)


# @app.route('/')
# def scraping_books():
#     url="https://books.toscrape.com/"
#     response=requests.get(url)
#     soup=BeautifulSoup(response.text,'html.parser')
#     books=soup.find_all('li',class_="article")

#     book_data = []
#     for book in books:
#         name = book.find('h3').find("a")
#         price = books.find("p",class_="price_color")

#         name = name.get('title')if name else None
#         price = price.get('price')if price else None

#         book_data.append([name],[price])
#     df = pd.DataFrame(book_data, columns=['Name', 'Price'])
#     return render_template('index.html', tables=df.to_html(index=False,classes="table table-striped"))

# #def index():
# #    return render_template('home.html')

# if __name__ == '__main__':
#     app.run(debug=True,port=3000,host="0.0.0.0")




from flask import Flask,render_template
from bs4 import BeautifulSoup
import pandas as pd
import requests


app=Flask(__name__)
# @app.route('/')
# def index():
#     return render_template("index.html")


@app.route('/')
def scrape_books():
        
    url="https://books.toscrape.com/"
    response=requests.get(url)
    soup=BeautifulSoup(response.content,'html.parser')


    product=[]
    items=soup.find_all("li",class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for i in items:
        name=i.find("h3").find("a")
        price=i.find("p",class_="price_color")

        Name=name.get("title") if name else None
        Price=price.get_text(strip=True) if price else None
        product.append([Name,Price])

    df=pd.DataFrame(product,columns=["Name","Price"])

    return render_template("home.html",Table=df.to_html(index=False,classes="table table-striped"))

if (__name__)== '__main__':
    app.run(debug=True,host="0.0.0.0",port=3000)