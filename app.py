from flask import Flask, render_template, redirect, url_for
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import re
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

scraped_data = pd.DataFrame()

# ✅ Home page with button
@app.route('/')
def index():
    return render_template("index.html")

# ✅ Scrape and show data
@app.route('/scrape')
def scrape_books():
    global scraped_data

    url = "https://books.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    product = []
    items = soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3")

    for i in items:
        name = i.find("h3").find("a")
        price = i.find("p", class_="price_color")

        Name = name.get("title") if name else None
        Price_text = price.get_text(strip=True) if price else None
        Price = float(re.sub(r'[^\d.]', '', Price_text)) if Price_text else None

        product.append([Name, Price])

    scraped_data = pd.DataFrame(product, columns=["Name", "Price"])

    return render_template("home.html", Table=scraped_data.to_html(index=False, classes="table table-striped"))

# ✅ Bar chart route
@app.route('/bar')
def bar_chart():
    if scraped_data.empty:
        return redirect('/scrape')

    plt.figure(figsize=(12, 6))
    plt.bar(scraped_data["Name"], scraped_data["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price")
    plt.title("Book Prices - Bar Chart")

    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()

    return render_template('bar_chart.html', chart_url=url_for('static', filename='chart.png'))

# ✅ Pie chart route
@app.route('/pie')
def pie_chart():
    if scraped_data.empty:
        return redirect('/scrape')

    bins = [0, 20, 40, 60, 80, 100, 1000]
    labels = ['0-20', '21-40', '41-60', '61-80', '81-100', '100+']
    scraped_data['Price Range'] = pd.cut(scraped_data['Price'], bins=bins, labels=labels)

    pie_data = scraped_data['Price Range'].value_counts().sort_index()

    plt.figure(figsize=(8, 8))
    plt.pie(pie_data, labels=pie_data.index, autopct='%1.1f%%', startangle=140)
    plt.title("Distribution of Book Prices")

    pie_chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'pie_chart.png')
    plt.savefig(pie_chart_path)
    plt.close()

    return render_template('pie_chart.html', chart_url=url_for('static', filename='pie_chart.png'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=3000)
