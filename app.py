from flask import Flask, render_template, url_for, redirect
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Must be before importing pyplot
import matplotlib.pyplot as plt
import os
import re 


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# Global DataFrame to hold scraped data
scraped_data = pd.DataFrame()

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/scraping')
def scraping():
    return render_template('scraping.html')

@app.route('/aboutMe')
def aboutMe():
    return render_template('about.html')

@app.route('/aboutCodroid')
def aboutCodroid():
    return render_template('aboutCodroid.html')

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/dataScience')
def dataScience():
    return render_template('scraping.html')

@app.route('/PowerBI')
def powerBI():
    return render_template('powerBI.html')

@app.route('/report/HR')
def report():
    return render_template("powerBIOpen.html", report_name="HR & Sales Analytics")

@app.route('/AIML')
def AIML():
    return render_template('comingSoon.html', page_name="AI/ML")

@app.route('/scrape')
def scrape_books():
    global scraped_data
    url = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    items = soup.find_all("article", class_="product_pod")

    for item in items:
        name_tag = item.find("h3").find("a")
        price_tag = item.find("p", class_="price_color")

        name = name_tag.get("title") if name_tag else "N/A"
        price = price_tag.get_text(strip=True) if price_tag else "£0"

        # inside the loop
        price_text = price_tag.get_text(strip=True) if price_tag else "£0"
        price_clean = re.sub(r"[^\d.]", "", price_text)   #$4.4 -> 4.4
        price = float(price_clean) if price_clean else 0.0


        products.append([name, price])

    scraped_data = pd.DataFrame(products, columns=["Name", "Price"])
    return render_template("index.html", table=scraped_data.to_html(index=False, classes="table table-striped"))

@app.route('/bar')
def bar_chart():
    if scraped_data.empty:
        return redirect('/scrape')

    plt.figure(figsize=(10, 6))
    plt.bar(scraped_data["Name"], scraped_data["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price (£)")
    plt.title("Book Prices - Bar Chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('bar_chart.html', chart_url=url_for('static', filename='chart.png'))




@app.route('/pie')
def pie_chart():
    if scraped_data.empty:
        return redirect('/scrape')

    top_books = scraped_data.sort_values(by="Price", ascending=False).head(5)
    plt.figure(figsize=(8, 8))
    plt.pie(top_books["Price"], labels=top_books["Name"], autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Most Expensive Science Books")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('pie_chart.html', chart_url=url_for('static', filename='chart.png'))

if __name__ == '__main__':
    app.run(debug=True, port=3000, host="0.0.0.0")
