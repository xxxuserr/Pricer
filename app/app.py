from flask import Flask, render_template, request
from scraper import search_product

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    products = []
    if request.method == "POST":
        query = request.form.get("query")
        if query:
            products = search_product(query)
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
