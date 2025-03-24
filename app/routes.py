from flask import render_template, request, jsonify
from app import app
from app.scraper import search_product
from flask import session
from flask import request, Response
from flask import redirect, request, flash, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from app.models import User
import requests
from app.models import FavoriteProduct


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
@login_required
def add_favorite():
    data = request.get_json()
    print("Date primite la server:", data)  # Verifică ce date sunt trimise
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'message': 'Date incomplete!'}), 400
    
    # Creăm un obiect FavoriteProduct
    new_product = FavoriteProduct(
        name=data['name'],
        price=data['price'],
        image=data.get('image', None),
        link=data.get('link', None),
        user_id=current_user.id  # Asigură-te că utilizatorul este autentificat
    )
    
    # Salvăm în baza de date
    db.session.add(new_product)
    try:
        db.session.commit()
        print("Produsul a fost adăugat cu succes!")
        return jsonify({'message': 'Produs adăugat la favorite!'}), 200
    except Exception as e:
        print(f"Eroare la salvarea în baza de date: {e}")
        db.session.rollback()  # Rolback în caz de eroare
        return jsonify({'message': 'Eroare la salvarea produsului!'}), 500




# Obține favoritele
@app.route('/get_favorites', methods=['GET'])
@login_required  # Asigură-te că utilizatorul este autentificat
def get_favorites():
    # Preluăm toate favoritele pentru utilizatorul curent
    favorite_products = FavoriteProduct.query.filter_by(user_id=current_user.id).all()
    
    # Creăm un răspuns cu lista produselor
    favorites_list = [{
        'name': product.name,
        'price': product.price,
        'image': product.image,
        'link': product.link
    } for product in favorite_products]
    
    return jsonify(favorites_list)


# Elimină din favorite
@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    data = request.get_json()
    session['favorites'] = [p for p in session.get('favorites', []) if p['name'] != data['name']]
    session.modified = True  # Marchează sesiunea ca modificată
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



