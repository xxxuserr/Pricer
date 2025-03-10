from flask import Flask

app = Flask(__name__)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cheie_secreta'  # Schimbă cu o cheie sigură
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Importă rutele după definirea `app`, `db` și `login_manager`
from app import routes, models