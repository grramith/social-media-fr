from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Initialize extensions such as Alchemy
db = SQLAlchemy()

# Create app instance
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

# Initializing extensions
db.init_app(app)

# Importing views
import website.views

# Database creation
with app.app_context():
    db.create_all()
