from flask import Flask, render_template, url_for, redirect,render_template_string
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # For headless servers
import matplotlib.pyplot as plt
# import yfinance as yf
import matplotlib.pyplot as plt
import io
from io import BytesIO
import os
import re 
import base64
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

# Global storage for different scrapers
scraped_data = {
    "books": pd.DataFrame(),
    "flipkart": pd.DataFrame(),
    "goodreads": pd.DataFrame(),
    "yahoo": pd.DataFrame(),
    "movies": pd.DataFrame()
}

# ------------------- Basic Pages -------------------
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/scraping')
def scraping():
    return render_template('scraping.html')

@app.route('/laptop_scraping')
def laptop_scraping():
    return render_template('laptop_scraping.html')



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

@app.route('/HR')
def HR():
    return render_template("HR.html")

@app.route('/Covid')
def Covid():
    return render_template("COVID.html")

@app.route('/netflix')
def Netflix():
    return render_template("netflix.html")

@app.route('/AIML')
def AIML():
    return render_template('comingSoon.html', page_name="AI/ML")



@app.route('/DataScience')
def DS():
    return render_template('DS.html', page_name="AI/ML")

@app.route('/DataScience')
def data_science():
    stock = "AAPL"  # Change ticker if needed
    start_date = "2022-01-01"
    end_date = "2023-12-31"

    try:
        data = yf.download(stock, start=start_date, end=end_date)
        if data.empty:
            raise ValueError("No data returned from yfinance.")
    except Exception as e:
        print("Failed to fetch stock data:", e)
        data = None

    # Generate plot if data is available
    img_base64 = ""
    if data is not None:
        plt.figure(figsize=(10,5))
        plt.plot(data['Close'], label='Closing Price')
        plt.title(f'{stock} Closing Price Over Time')
        plt.xlabel('Date')
        plt.ylabel('Price(USD)')
        plt.legend()
        plt.grid(True)

        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close()

    # Data summary
    summary = data.describe().to_html() if data is not None else "<p>Data not available</p>"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{stock} Stock Price</title>
    </head>
    <body>
        <h1>{stock} Closing Price</h1>
        <p>Data from {start_date} to {end_date}</p>
        {'<img src="data:image/png;base64,' + img_base64 + '" alt="Stock Plot"/>' if img_base64 else '<p>Plot not available</p>'}
        <h2>Data Summary</h2>
        {summary}
    </body>
    </html>
    """
    return render_template_string(html_content)


# ===================================================
# ------------------- Book Scraping ----------------
# ===================================================
@app.route('/scrape')
def scrape_books():
    url = "https://books.toscrape.com/catalogue/category/books/science_22/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    items = soup.find_all("article", class_="product_pod")

    for item in items:
        name_tag = item.find("h3").find("a")
        price_tag = item.find("p", class_="price_color")

        name = name_tag.get("title") if name_tag else "N/A"
        price_text = price_tag.get_text(strip=True) if price_tag else "£0"
        price_clean = re.sub(r"[^\d.]", "", price_text)
        price = float(price_clean) if price_clean else 0.0

        products.append([name, price])

    scraped_data["books"] = pd.DataFrame(products, columns=["Name", "Price"])
    return render_template("index.html", 
                           table=scraped_data["books"].to_html(index=False, classes="table table-striped"))

@app.route('/bar')
def bar_chart():
    if scraped_data["books"].empty:
        return redirect('/scrape')

    plt.figure(figsize=(10, 6))
    plt.bar(scraped_data["books"]["Name"], scraped_data["books"]["Price"])
    plt.xticks(rotation=90)
    plt.ylabel("Price (£)")
    plt.title("Book Prices - Bar Chart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_books.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('bar_chart.html', chart_url=url_for('static', filename='chart_books.png'))

@app.route('/pie')
def pie_chart():
    if scraped_data["books"].empty:
        return redirect('/scrape')

    top_books = scraped_data["books"].sort_values(by="Price", ascending=False).head(5)
    plt.figure(figsize=(8, 8))
    plt.pie(top_books["Price"], labels=top_books["Name"], autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Most Expensive Science Books")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_books.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('pie_chart.html', chart_url=url_for('static', filename='chart_books.png'))

# ===================================================
# ------------------- Flipkart Laptops --------------
# ===================================================
@app.route('/scrape_flipkart')
def scrape_flipkart():
    url = "https://www.flipkart.com/search?q=laptop"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    products = []
    items = soup.find_all("div", class_="_75nlfW")
    for item in items:
        name_tag = item.find("div", class_="KzDlHZ")
        price_tag = item.find("div", class_="_4b5DiR")
        rating_tag = item.find("div", class_="XQDdHH")

        if name_tag and price_tag:
            name = name_tag.get_text(strip=True)
            brand = name.split()[0] if name else "Unknown"

            price_text = price_tag.get_text(strip=True)
            price_clean = re.sub(r"[^\d]", "", price_text)
            price = float(price_clean) if price_clean else 0.0

            rating = rating_tag.get_text(strip=True) if rating_tag else "0"
            try:
                rating = float(rating)
            except:
                rating = 0.0

            products.append([brand, name, price, rating])

    scraped_data["flipkart"] = pd.DataFrame(products, columns=["Brand", "Name", "Price (₹)", "Rating"])
    return render_template("laptop_scraping.html", 
                           laptops=scraped_data["flipkart"].to_dict(orient="records"))

@app.route('/bar_flipkart')
def bar_chart_flipkart():
    if scraped_data["flipkart"].empty:
        return redirect('/scrape_flipkart')

    plt.figure(figsize=(12, 6))
    top_laptops = scraped_data["flipkart"].sort_values(by="Price (₹)", ascending=False).head(10)
    plt.bar(top_laptops["Name"], top_laptops["Price (₹)"], color='skyblue')
    plt.xticks(rotation=90)
    plt.ylabel("Price (₹)")
    plt.title("Top 10 Most Expensive Laptops - Flipkart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_flipkart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('laptop_bar_chart.html', chart_url=url_for('static', filename='chart_flipkart.png'))

@app.route('/pie_flipkart')
def pie_chart_flipkart():
    if scraped_data["flipkart"].empty:
        return redirect('/scrape_flipkart')

    top_laptops = scraped_data["flipkart"].sort_values(by="Price (₹)", ascending=False).head(5)
    plt.figure(figsize=(8, 8))
    plt.pie(top_laptops["Price (₹)"], labels=top_laptops["Name"], autopct="%1.1f%%", startangle=140)
    plt.title("Top 5 Most Expensive Laptops - Flipkart")
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'chart_flipkart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('laptop_pie_chart.html', chart_url=url_for('static', filename='chart_flipkart.png'))

# ===================================================
# ------------------- Goodreads ---------------------
# ===================================================
@app.route('/scrape_goodreads')
def scrape_goodreads():
    url = "https://www.goodreads.com/quotes"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    quotes = []
    for q in soup.find_all("div", class_="quoteText"):
        text = q.get_text(strip=True, separator=" ")
        quotes.append(text)

    scraped_data["goodreads"] = pd.DataFrame(quotes, columns=["Quote"])
    return render_template(
        "goodreads.html", 
        data=scraped_data["goodreads"].to_html(classes="styled-table", index=False, border=0)
    )


@app.route('/goodreads_bar')
def goodreads_bar():
    if scraped_data["goodreads"].empty:
        return redirect('/scrape_goodreads')

    df = scraped_data["goodreads"].copy()
    df["Author"] = df["Quote"].apply(lambda x: x.split("―")[-1].strip() if "―" in x else "Unknown")
    author_counts = df["Author"].value_counts().head(10)

    plt.figure(figsize=(10, 5))
    author_counts.plot(kind='bar', color='cyan', edgecolor='black')
    plt.title("Top Authors by Quote Count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    chart_path = "static/goodreads_bar.png"
    plt.savefig(chart_path)
    plt.close()
    return render_template("goodreads_bar_chart.html", chart_path=chart_path)

@app.route('/goodreads_pie')
def goodreads_pie():
    if scraped_data["goodreads"].empty:
        return redirect('/scrape_goodreads')

    df = scraped_data["goodreads"].copy()
    df["Author"] = df["Quote"].apply(lambda x: x.split("―")[-1].strip() if "―" in x else "Unknown")
    author_counts = df["Author"].value_counts().head(5)

    plt.figure(figsize=(6, 6))
    author_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, shadow=True)
    plt.title("Top Authors by Quote Share")
    plt.ylabel("")
    chart_path = "static/goodreads_pie.png"
    plt.savefig(chart_path)
    plt.close()
    return render_template("goodreads_pie_chart.html", chart_path=chart_path)

# ===================================================
# ------------------- Yahoo Finance -----------------
# ===================================================
# ---------------- Helper Function ----------------
def get_yahoo_funds():
    url = "https://finance.yahoo.com/markets/mutualfunds/top/?start=0&count=25"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    funds = []
    rows = soup.find_all("tr", class_="yf-7uw1qi")
    
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 7:
            name = cols[0].get_text(strip=True)
            last_price = cols[1].get_text(strip=True)
            change = cols[2].get_text(strip=True)
            percent_change = cols[3].get_text(strip=True)
            fund_type = cols[4].get_text(strip=True)
            assets = cols[5].get_text(strip=True)
            yield_ = cols[6].get_text(strip=True)
            
            funds.append({
                "Name": name,
                "Last Price": last_price,
                "Change": change,
                "% Change": percent_change,
                "Type": fund_type,
                "Assets": assets,
                "Yield": yield_
            })
    return funds

# ---------------- Routes ----------------
@app.route('/scrape_yahoo')
def scrape_yahoo():
    funds = get_yahoo_funds()
    return render_template("yahoo.html", funds=funds)

# ----------- Bar Chart Route -------------
@app.route('/bar_chart_yahoo')
def bar_chart_yahoo():
    funds = get_yahoo_funds()  # function to fetch Yahoo mutual funds data
    top_funds = sorted(funds, key=lambda x: x['Assets'], reverse=True)[:10]

    names = [f['Name'] for f in top_funds]
    assets = [f['Assets'] for f in top_funds]

    plt.figure(figsize=(10,6))
    plt.barh(names[::-1], assets[::-1], color='#00f0ff')
    plt.xlabel('Assets (in Billions $)')
    plt.title('Top 10 Mutual Funds by Assets')
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('yahoo_bar_chart.html', chart_url='data:image/png;base64,{}'.format(plot_url))



# ----------- Pie Chart Route -------------
@app.route('/pie_chart_yahoo')
def pie_chart_yahoo():
    funds = get_yahoo_funds()
    # Convert Assets to float
    for f in funds:
        f['Assets_float'] = float(f['Assets'].replace(',','').replace('$',''))
    top_funds = sorted(funds, key=lambda x: x['Assets_float'], reverse=True)[:10]

    names = [f['Name'] for f in top_funds]
    assets = [f['Assets_float'] for f in top_funds]

    plt.figure(figsize=(8,8))
    plt.pie(assets, labels=names, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title('Top 10 Mutual Funds by Assets')
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png', transparent=True)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return render_template('yahoo_pie_chart.html', chart_url='data:image/png;base64,{}'.format(plot_url))

# ===================================================
# ------------------- IMDb Movies ------------------
# ===================================================

@app.route('/scrape_movies')
def scrape_movies():
    url = "https://www.imdb.com/chart/top/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    rows = soup.find_all("div", class_="sc-ec40e84d-1 dwYbao cli-parent li-compact")
    movies = []
    title = []
    rating = []

    for row in rows:
        title_column = row.find("h3", class_="ipc-title__text ipc-title__text--reduced")
        rating_column = row.find("span", class_="ipc-rating-star--rating")
        title = title_column.text
        rating = rating_column.text
        movies.append({
            "title": title,
            "rating": rating
        })
    return render_template("movies.html", movies= movies)


@app.route('/bar_movies')
def movie_bar_chart():
    if scraped_data["movies"].empty:
        return redirect('/scrape_imdb')

    plt.figure(figsize=(10,6))
    plt.barh(scraped_data["movies"]["Title"], scraped_data["movies"]["Rating"], color='orange')
    plt.xlabel('Rating')
    plt.title('Top 10 IMDb Movies - Ratings')
    plt.gca().invert_yaxis()
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'movies_bar_chart.png')
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    return render_template('movies_bar_chart.html',
                           chart_url=url_for('static', filename='movies_bar_chart.png'))

@app.route('/pie_movies')
def movie_pie_chart():
    if scraped_data["movies"].empty:
        return redirect('/scrape_imdb')

    plt.figure(figsize=(8,8))
    plt.pie(scraped_data["movies"]["Rating"], labels=scraped_data["movies"]["Title"],
            autopct='%1.1f%%', startangle=140)
    plt.title('Top 10 IMDb Movies - Rating Distribution')
    chart_path = os.path.join(app.config['UPLOAD_FOLDER'], 'movies_pie_chart.png')
    plt.savefig(chart_path)
    plt.close()
    return render_template('movies_pie_chart.html',
                           chart_url=url_for('static', filename='movies_pie_chart.png'))


# ===================================================
if __name__ == '__main__':
    app.run(debug=True, port=3000, host="0.0.0.0")
