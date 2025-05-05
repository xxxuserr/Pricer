from app import app, db
from app.models import PriceAlert, User
from app.scraper import get_price_from_link
from app.email_utils import send_email_alert
from flask_apscheduler import APScheduler
import time

# 🔁 Funcția care verifică alertele și trimite email dacă s-a schimbat prețul
def check_alerts():
    with app.app_context():  # ← Asta rezolvă problema
        alerts = PriceAlert.query.filter_by(active=True).all()

        for alert in alerts:
            current_price = get_price_from_link(alert.link)
            if current_price is None:
                continue

            if current_price != alert.initial_price:
                user = db.session.get(User, alert.user_id)

                if current_price != alert.initial_price:
                    user = db.session.get(User, alert.user_id)

                    if user and user.email:
                        send_email_alert(
                            to_email=user.email,
                            subject=f"🔔 Preț modificat la {alert.product_name}",
                            body=(
                                f"Noul preț este {current_price} lei (anterior: {alert.initial_price}).\n"
                                f"Link: {alert.link}"
                            )
                        )
                    print(f"[ALERTĂ TRIMISĂ] Utilizator: {user.email} | Produs: {alert.product_name} | Preț nou: {current_price} lei")

                    alert.initial_price = current_price
                    alert.active = False
                    db.session.commit()
                    time.sleep(1)

# 🕓 Configurare și pornire scheduler
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# ⚙️ Programăm verificarea alertelor la fiecare 30 minute
scheduler.add_job(id='CheckPriceAlerts', func=check_alerts, trigger='interval', minutes=1)

# ▶️ Pornim serverul Flask
if __name__ == "__main__":
    app.run(debug=True)
