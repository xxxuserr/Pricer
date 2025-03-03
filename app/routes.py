from flask import render_template, request, jsonify
from app import app
from app.scraper import search_product
from flask import session

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

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    data = request.get_json()
    if 'favorites' not in session:
        session['favorites'] = []

    # Verifică dacă produsul există deja
    for product in session['favorites']:
        if product['name'] == data['name']:
            return jsonify({'message': 'Produsul este deja în favorite!'}), 400

    session['favorites'].append(data)
    session.modified = True
    return jsonify({'message': 'Produs adăugat la favorite!'}), 200

# Obține favoritele
@app.route('/get_favorites')
def get_favorites():
    return jsonify(session.get('favorites', []))

# Elimină din favorite
@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    data = request.get_json()
    session['favorites'] = [p for p in session.get('favorites', []) if p['name'] != data['name']]
    session.modified = True
    return jsonify({'message': 'Produs eliminat din favorite!'}), 200

@app.route("/favorites")
def favorites():
    favorites = session.get('favorites', [])  # Preia favoritele din sesiune
    return render_template("favorites.html", favorites=favorites)
