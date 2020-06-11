import os
from dotenv import load_dotenv
from flask import Flask, Blueprint, jsonify, request, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from web_app.routes import my_routes
from web_app.models import db, migrate, User, Repos

load_dotenv()

# database url as an environment variable
#DATABASE_URL = os.getenv("DATABASE_URL", default="OOPS")

# database URL direct, needs to be fixed**
DATABASE_URL = "sqlite://///web_app/git_test.db"

def create_app():

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # importing models.py database class tables
    # links to __init__file which calls on create app to run
    db.init_app(app)
    migrate.init_app(app, db)
    
    # linking to routes.py page via my_routes variable
    app.register_blueprint(my_routes)

    return app
