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
from app.models import PriceAlert
from run import check_alerts

cached_data = {}

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
    print("Date primite de la client:", data)

    if not data or 'name' not in data or 'price' not in data:
        return jsonify({'message': 'Date incomplete!'}), 400

    try:
        new_product = FavoriteProduct(
            name=data['name'],
            price=data['price'],
            image=data.get('image', None),
            link=data.get('link', None),
            user_id=current_user.id
        )
        db.session.add(new_product)

        existing_alert = PriceAlert.query.filter_by(
            user_id=current_user.id,
            product_name=data['name']
        ).first()

        if not existing_alert:
            new_alert = PriceAlert(
                user_id=current_user.id,
                product_name=data['name'],
                initial_price=float(data['price']),
                link=data['link'],
                image=data['image'],
                active=False 
            )
            db.session.add(new_alert)

        db.session.commit()
        return jsonify({'message': 'Produs adăugat la favorite!'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"❌ Eroare la salvare: {e}")
        return jsonify({'message': f'Eroare la salvare: {e}'}), 500



# Elimină din favorite
@app.route('/remove_favorite', methods=['POST'])
def remove_favorite():
    data = request.get_json()

    # Căutăm produsul după nume și îl ștergem din baza de date
    product_to_remove = FavoriteProduct.query.filter_by(name=data['name'], user_id=current_user.id).first()

    if product_to_remove:
        db.session.delete(product_to_remove)
        db.session.commit()
        return jsonify({'message': 'Produs eliminat din favorite!'}), 200
    else:
        return jsonify({'message': 'Produsul nu a fost găsit în favorite!'}), 404


@app.route("/favorites")
@login_required
def favorites():
    favorite_products = FavoriteProduct.query.filter_by(user_id=current_user.id).all()

    favorites_list = []

    for product in favorite_products:
        alert = PriceAlert.query.filter_by(
            user_id=current_user.id,
            link=product.link,
            active=True
        ).first()

        favorites_list.append({
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'link': product.link,
            'alert_active': bool(alert)  # ← aici apare dacă e activă alerta
        })

    return render_template("favorites.html", favorites=favorites_list)



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


@app.route('/set_alert', methods=['POST'])
@login_required
def set_alert():
    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    link = data.get('link')
    image = data.get('image')

    if not all([name, price, link]):
        return jsonify({'message': 'Date incomplete!'}), 400

    # Verificăm dacă există deja o alertă pentru același link
    alert = PriceAlert.query.filter_by(
        user_id=current_user.id,
        link=link
    ).first()

    if alert:
        if alert.active:
            return jsonify({'message': f'Alerta pentru „{name}” este deja activă.'})
        else:
            alert.active = True
            db.session.commit()
            return jsonify({'message': f'Alerta pentru „{name}” a fost activată.'})

    # Dacă nu există alertă, creăm una nouă
    new_alert = PriceAlert(
        user_id=current_user.id,
        product_name=name,
        initial_price=float(price),
        link=link,
        image=image,
        active=True
    )

    db.session.add(new_alert)
    db.session.commit()

    return jsonify({'message': f'Alerta pentru „{name}” a fost setată cu succes.'})

@app.route('/disable_alert', methods=['POST'])
@login_required
def disable_alert():
    data = request.get_json()
    link = data.get('link')

    if not link:
        return jsonify({'message': 'Lipsă link produs.'}), 400

    alert = PriceAlert.query.filter_by(user_id=current_user.id, link=link, active=True).first()

    if alert:
        alert.active = False
        db.session.commit()
        return jsonify({'message': f'Alerta pentru „{alert.product_name}” a fost dezactivată.'})
    else:
        return jsonify({'message': 'Nu există alertă activă pentru acest produs.'}), 404


@app.route('/run_alert_check', methods=['POST'])
@login_required
def run_alert_check():
    try:
        check_alerts()
        return jsonify({'message': 'Verificarea alertelor a fost rulată cu succes!'})
    except Exception as e:
        return jsonify({'message': f'Eroare la rularea verificării: {str(e)}'}), 500