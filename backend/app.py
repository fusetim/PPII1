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
from search_table import save_search_tables, get_recipe_table, get_ingredient_table
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

@app.route("/home", methods=("GET",))
def home():
    """
    home page with an "about" section and a search bar to question the "ingredients" db
    """
    return render_template("home.html")

@app.route("/result_ingredients")
def result_ingredients():
    """
    a page showing the results of the research from the home page
    shows ingredients' names and co2 equivalent cost
    """
    search = request.args.get("search")
    table = get_ingredient_table()
    normalized_query = normalize_str(search)
    codes = table.get(normalized_query, 10)
    data = []
    if codes == []:
        return render_template("no_result.html")
    else:
        for code in codes:
            #.all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            ingr = db.session.execute(text("SELECT name, co2 FROM ingredients WHERE code = :c"), {'c' : code}).all()[0]
            data.append(ingr)
        return render_template("result_ingredients.html", data=data)

@app.route("/recipes", methods=("GET",))
def recipes():
    """
    a page showing a search bar to question the "recipes" db
    """
    return render_template("recipes.html")
"""
@app.route("/result_recipes", methods=("GET",))
def result_recipes():
    search = request.args.get("search")
    table = get_recipe_table()
    normalized_query = normalize_str(search)
    codes = table.get(normalized_query, 10)
    data = []
    if codes == []:
        return render_template("no_result.html")
    else:
        for code in codes:
            #.all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            ingr = db.session.execute(text("SELECT name FROM Recipe WHERE recipe_uid = :c"), {'c' : code}).all()[0]
            data.append(ingr)
        #return render_template("result_recipes.html", data=data)
        return str(ingr)
"""
