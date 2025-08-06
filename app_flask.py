## Flask App Routing





# from flask import Flask

# app=Flask(__name__)

# @app.route('/',methods=["GET"])
# def welcome():
#     return "Welcome to my Flask App"

# @app.route('/index',methods=["GET"])
# def index():
#     return "<h1>This is the index page of my Flask App</h1>"

# if __name__=="__main__":
#     app.run(debug=True)










from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
import pandas as pd

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape')
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

if __name__ == '__main__':
    app.run(debug=True)

# @app.route('/index')
# def scrape_flipkart():
#     url = "https://www.flipkart.com/search?q=laptop"
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#     }

#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     laptops = []
#     items = soup.find_all("div", class_="tUxRFH")  # main container

#     for item in items:
#         title_tag = item.find("div", class_="KzDlHZ")
#         price_tag = item.find("div", class_="Nx9bqj _4b5DiR")
#         rating_tag = item.find("div", class_="XQDdHH")

#         if title_tag and price_tag:
#             title = title_tag.get_text(strip=True)
#             price = price_tag.get_text(strip=True)
#             rating = rating_tag.get_text(strip=True) if rating_tag else "No Rating"

#             laptops.append({"Title": title, "Price": price, "Rating": rating})

#     # Create DataFrame
#     df = pd.DataFrame(laptops)

#     return render_template("index.html", title="Laptop Data", tables=df.to_html(classes="table table-striped", index=False))


