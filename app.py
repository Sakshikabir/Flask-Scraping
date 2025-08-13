from flask import Flask, render_template, redirect, url_for
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

BOOKS_CSV = 'books.csv'
LAPTOPS_CSV = 'laptops.csv'

@app.route('/')
def intro():
    return render_template('intro.html')

# ✅ Home page
@app.route('/index')
def index():
    return render_template("index.html")

# ✅ Scrape books
@app.route('/scrape')
def scrape_books():
    url = "https://books.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []
    items = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for i in items:
        name = i.find("h3").find("a")
        price = i.find("p", class_="price_color")

        Name = name.get("title") if name else None
        Price_text = price.get_text(strip=True) if price else None
        Price = float(re.sub(r'[^\d.]', '', Price_text)) if Price_text else None

        products.append([Name, Price])

    df_books = pd.DataFrame(products, columns=["Name", "Price"])
    df_books.to_csv(BOOKS_CSV, index=False)

    return render_template("home.html", Table=df_books.to_html(index=False, classes="table table-striped"), data_type="books")

# ✅ Bar chart for books
@app.route('/bar')
def bar_chart():
    if not os.path.exists(BOOKS_CSV):
        return redirect('/scrape')

    df_books = pd.read_csv(BOOKS_CSV)
    plt.figure(figsize=(12, 6))
    plt.bar(df_books["Name"], df_books["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price")
    plt.title("Book Prices - Bar Chart")

    chart_name = f'chart_books_{int(time.time())}.png'
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_name)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return render_template('bar_chart.html', chart_url=url_for('static', filename=chart_name))

# ✅ Pie chart for books
@app.route('/pie')
def pie_chart():
    if not os.path.exists(BOOKS_CSV):
        return redirect('/scrape')

    df_books = pd.read_csv(BOOKS_CSV)
    bins = [0, 20, 40, 60, 80, 100, 1000]
    labels = ['0-20', '21-40', '41-60', '61-80', '81-100', '100+']
    df_books['Price Range'] = pd.cut(df_books['Price'], bins=bins, labels=labels)

    pie_data = df_books['Price Range'].value_counts().sort_index()

    plt.figure(figsize=(8, 8))
    plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
    plt.title("Distribution of Book Prices")

    pie_chart_name = f'pie_books_{int(time.time())}.png'
    pie_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], pie_chart_name)
    plt.savefig(pie_chart_path)
    plt.close()

    return render_template('pie_chart.html', chart_url=url_for('static', filename=pie_chart_name))

# ✅ Flipkart laptop scraper 
@app.route('/flipkart')
def flipkart():
    url = "https://www.flipkart.com/search?q=laptop&sid=6bo%2Cb5g&as=on&as-show=on"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    laptops = []
    items = soup.find_all("div", class_="tUxRFH")

    for i in items:
        name = i.find("div", class_="KzDlHZ")
        price = i.find("div", class_="Nx9bqj _4b5DiR")
        rating = i.find("div", class_="XQDdHH")

        if not name or not price:
            continue

        title = name.get_text(strip=True)
        Price_text = price.get_text(strip=True).replace(',', '')
        try:
            Price = float(re.sub(r'[^\d.]', '', Price_text))
        except:
            Price = None
        Rating = rating.get_text(strip=True) if rating else None

        laptops.append([title, Price, Rating])

    df_laptops = pd.DataFrame(laptops, columns=["Name", "Price", "Rating"])
    df_laptops.to_csv(LAPTOPS_CSV, index=False)

    return render_template("home.html", Table=df_laptops.to_html(index=False, classes="table table-striped"),data_type="laptops")

# ✅ Bar chart for laptops
@app.route('/bar_laptop')
def bar_chart_laptop():
    if not os.path.exists(LAPTOPS_CSV):
        return redirect('/flipkart')

    df_laptops = pd.read_csv(LAPTOPS_CSV)
    df_laptops["Price"] = pd.to_numeric(df_laptops["Price"], errors='coerce').fillna(0)

    plt.figure(figsize=(12, 6))
    plt.bar(df_laptops["Name"], df_laptops["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price")
    plt.title("Laptop Prices - Bar Chart")

    chart_name = f'chart_laptops_{int(time.time())}.png'
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], chart_name)
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return render_template('bar_chart_laptop.html', chart_url=url_for('static', filename=chart_name))

# ✅ Pie chart for Flipkart laptops
@app.route('/pie_laptop')
def pie_chart_laptop():
    if not os.path.exists(LAPTOPS_CSV):
        return redirect('/flipkart')

    df_laptops = pd.read_csv(LAPTOPS_CSV)

    # Define price bins
    bins = [0, 20000, 40000, 60000, 80000, 100000, 1000000]
    labels = ['0-20k', '20k-40k', '40k-60k', '60k-80k', '80k-1L', '1L+']
    df_laptops['Price Range'] = pd.cut(df_laptops['Price'], bins=bins, labels=labels)

    pie_data = df_laptops['Price Range'].value_counts().sort_index()

    plt.figure(figsize=(8, 8))
    plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
    plt.title("Distribution of Laptop Prices")

    pie_chart_name = f'pie_laptops_{int(time.time())}.png'
    pie_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], pie_chart_name)
    plt.savefig(pie_chart_path)
    plt.close()

    return render_template('pie_chart_laptop.html', chart_url=url_for('static', filename=pie_chart_name))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
