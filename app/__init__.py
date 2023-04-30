from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS

# App Config
app = Flask(__name__, )
app.config.from_object('config')
db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)


# Celery
from app.celery import make_celery
celery = make_celery(app)

# Database
from config import secret
app.secret_key = secret
migrate = Migrate(app, db)


# Controllers
from app.user.controller import bp as user_bp
app.register_blueprint(user_bp)
from app.dispatch.controller import bp as dispatch_bp
app.register_blueprint(dispatch_bp)
from app.customer.controller import bp as customer_bp
app.register_blueprint(customer_bp)
from app.delivery.controller import bp as delivery_bp
app.register_blueprint(delivery_bp)

# Error handlers
from .error_handlers import *