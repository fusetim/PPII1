from api import api
from flask import Flask, render_template, request, redirect
import tomllib
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import models
from flask import g
import os
import sys
from db import db
from search_table import save_search_tables, get_ingredient_table
from lsh import normalize_str

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
        search = request.form["search"]
        table = get_ingredient_table()
        normalized_query = normalize_str(search)
        codes = table.get(normalized_query, 10)
        data = []
        if codes == []:
            return render_template("aucun_res.html")
        else:
            for code in codes:
                #.all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
                ingr = db.session.execute(text("SELECT name, co2 FROM ingredients WHERE code = :c"), {'c' : code}).all()[0]
                data.append(ingr)
            return render_template("res_ingredients.html", data=data)
    if request.method == "GET":
        return render_template("accueil.html")
