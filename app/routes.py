from flask import render_template, request, jsonify
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

@app.route("/search")
def search():
    query = request.args.get("query", "").lower()  # Preia query-ul din URL
    results = search_product(query)

    return jsonify(results)  # Răspunde cu un JSON ce conține produsele găsite
