from flask import render_template, request
from app import app
from app.scraper import search_product

@app.route("/", methods=["GET", "POST"])
def index():
    products = []
    
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            products = search_product(query)

    return render_template("index.html", products=products)