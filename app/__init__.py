# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Inițializarea aplicației Flask
app = Flask(__name__)

# Configurarea bazei de date
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc://user_pricer:12345678@DONTLOOK/pricer_db?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '4f3c8b5d0c8c3e5e02e9fbb40a6b4b1f785c62cb7311fdb9c1b3c8d4e8e1a92e'

# Inițializarea bazei de date
db = SQLAlchemy(app)

# Inițializarea LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Inițializarea Bcrypt
bcrypt = Bcrypt()

# Importarea modelelor și rutelor
from app import routes, models


