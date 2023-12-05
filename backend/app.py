from api import api
from flask import Flask, render_template, request
import tomllib
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import models
from flask import g
import os
import sys
from db import db
from search_table import save_search_tables

# Add the root directory to the PYTHONPATH
p = os.path.abspath(".")
sys.path.insert(1, p)

# Entrypoint for the Flask app.
app = Flask(__name__)
# Register the `/api` routes
app.register_blueprint(api, url_prefix="/api")
# Load the config file
app.config.from_file("config.toml", load=tomllib.load, text=False)
# Initialize the database
db.init_app(app)
# Initialize the migration engine (for database migrations)
migrate = Migrate(app, db)

# On app teardown, save the LSH tables.
app.teardown_appcontext(save_search_tables)

# By default, Flask already routes the static directory :)
# No need for a dedicated route.


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/accueil", methods=("GET", "POST"))
def accueil():
    if request.method == "POST":
        return request.form["search"]
    if request.method == "GET":
        return render_template("accueil.html")