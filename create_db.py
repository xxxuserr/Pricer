from app import app, db

# Crează tabelele în baza de date
with app.app_context():
    db.create_all()  # Crează tabelele în baza de date

print("Tabelele au fost create cu succes!")
