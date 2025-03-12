from flask import render_template, request, jsonify
from app import app
from app.scraper import search_product
from flask import session

from flask import redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User


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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first():
            flash("Acest email este deja folosit!", "danger")
            return redirect(url_for("register"))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Cont creat cu succes! Acum poți să te autentifici.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Autentificare reușită!", "success")
            return redirect(url_for("index"))
        else:
            flash("Email sau parolă incorecte!", "danger")

    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html", user=current_user)

@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    current_user.username = request.form.get("username")
    db.session.commit()
    flash("Profil actualizat cu succes!", "success")
    return redirect(url_for("profile"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Te-ai deconectat!", "info")
    return redirect(url_for("login"))