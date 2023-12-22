from api import api
from views import views
from flask import Flask, render_template, request, url_for
import tomllib
from sqlalchemy import text
from flask_migrate import Migrate
import os
import sys
from db import db
from search_table import save_search_tables, get_ingredient_table
from lsh import normalize_str
from models.recipe import Recipe
from models.ingredient_link import IngredientLink
from models.ingredient import Ingredient
from math import floor
from md_render import markdown_render
from util.human_format import format_duration, format_mass
from util.upload_helper import get_upload_url
from login import login_manager

# Add the root directory to the PYTHONPATH
p = os.path.abspath(".")
sys.path.insert(1, p)

# Entrypoint for the Flask app.
app = Flask(__name__)
# Register the `/api` & views routes
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(views, url_prefix="/")
# Load the config file
app.config.from_file("config.toml", load=tomllib.load, text=False)
# Initialize the database
db.init_app(app)
# Initialize the migration engine (for database migrations)
migrate = Migrate(app, db)
# Initialize the login manager
login_manager.init_app(app)

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


@app.route("/search_ingredients")
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
            # .all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            ingr = db.session.execute(
                text("SELECT name, co2 FROM ingredients WHERE code = :c"), {"c": code}
            ).all()[0]
            data.append(ingr)
        return render_template("result_ingredients.html", data=data)


@app.route("/recipes")
def recipes():
    """
    a page showing a search bar to question the "recipes" db
    """
    return render_template("recipes.html")


@app.route("/recipe/<uuid:recipe_uid>")
def get_recipe(recipe_uid):
    """
    a page displaying the recipe with the given id
    """

    def ingr_mass_equivalent(link: IngredientLink):
        """
        Compute the mass equivalent of an ingredient link.

        If the link has a reference quantity, it is prefered, otherwise we fallbalk on an
        equivalent based on the quantity type.
        """
        if link.reference_quantity is not None:
            return link.reference_quantity
        else:
            return link.quantity_type.mass_equivalent * link.quantity

    # Looking for our recipe
    recipe = db.session.get(Recipe, recipe_uid)
    if recipe is None:
        raise ("Recipe not found.", 404)

    # Looking for the ingredients
    links = db.session.query(IngredientLink).filter_by(recipe_uid=recipe_uid).all()

    # Computing the carbon score
    carbon_score = sum(map(lambda l: ingr_mass_equivalent(l) * l.ingredient.co2, links))

    # Building the ingredients list (and comuting the carbon part)
    ingr_info = [
        {
            "name": l.display_name,
            "quantity": l.quantity,
            "unit": l.quantity_type.unit,
            "carbon_part": ingr_mass_equivalent(l)
            * l.ingredient.co2
            / carbon_score
            * 100,
        }
        for l in links
    ]
    ingr_info.sort(key=lambda x: x["carbon_part"], reverse=True)

    # Building the tags list to display
    tags_list = [tag.name for tag in recipe.tags]

    # Format carbon_score
    score, score_unit = format_mass(carbon_score / 4)
    return render_template(
        "recipe.html",
        title=recipe.name,
        duration=format_duration(recipe.duration * 60),
        tags=tags_list,
        ingredients=ingr_info,
        carbon_score=score,
        score_unit=score_unit,
        recipe=markdown_render(recipe.description),
        cover=get_upload_url(recipe.illustration),
    )
