from api import api
from views import views
from flask import Flask, render_template, request, url_for, redirect
import tomllib
from sqlalchemy import text
from flask_migrate import Migrate
import os
import sys
from db import db
from search_table import save_search_tables, get_ingredient_table, get_recipe_table
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
    return redirect("/home")


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
    other = db.session.execute(
                text(f"SELECT name, co2 FROM ingredients WHERE normalized_name LIKE '%{normalized_query}%'")
            ).all()
    if search == "":
        return render_template("result_ingredients.html", data=data, search=search)
    
    elif codes == [] and other == []:
        return render_template("no_result_ingredients.html", search=search)
    else:
        for code in codes:
            # .all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            ingr = db.session.execute(
                text("SELECT name, co2 FROM ingredients WHERE code = :c"), {"c": code}
            ).all()[0]
            # on arondit le score co2
            ingr = (ingr[0], round(ingr[1], 2))
            data.append(ingr)
        if search != "":
            for r in other:
                if r not in data:
                    # on arondit le score co2
                    r = (r[0], round(r[1], 2))
                    #data.append(r)
                    data.insert(0, r)
        sort_type = request.args.get("sort_type")
        if sort_type in (None, ""):
            sort_type = 0
        else:
            sort_type = int(sort_type)
        
        # on trie data comme voulu (0 : par nom ; 1 par co2 croissant ; 2 par co2 decroissant)
        if sort_type == 0:
            data.sort(key= lambda a:a[0])
            co2sort = 2
            triangle = ""
        elif sort_type == 1:
            data.sort(key=lambda a:a[1], reverse=False)
            co2sort = 2
            triangle = "▲"
        else :
            data.sort(key=lambda a:a[1], reverse=True)
            co2sort = 1
            triangle = "▼"
        # nbres : nb de resultats affichés sur une meme page
        nbres=10

        if len(data)<=nbres:
            arrows = """<section class="arrows">1 sur 1</section>"""
            return render_template("result_ingredients.html", 
                                   data=data, search=search,
                                   produit="Produit", 
                                   m1=f"équivalent co2    {triangle}", 
                                   m2="par kg de produit", 
                                   co2sort=co2sort,
                                   sort_type=sort_type,
                                   f1="<",
                                   f2=">",
                                   sur="sur",
                                   lf1="#", 
                                   cf1="nolink", 
                                   lf2="#", 
                                   cf2="nolink", 
                                   numero="1", 
                                   n_total="1")
        else:
            page = request.args.get("page")
            if page == None:
                page = 1
            else : 
                page = int(page)

            # on recrée le format mot1+mo2+... pour ne pas que au passage d'une page à l'autre
            # on ne garde que le premier mot de la recherche (pour qu'il n'y ait pas d'espace dans l'url)
            query = ""
            for c in search:
                if c == " ":
                    query += "+"
                else:
                    query += c
            if page == 1:
                return render_template("result_ingredients.html", 
                                   data=data[:nbres], search=search, query=query,
                                   produit="Produit",
                                   m1=f"équivalent co2    {triangle}", 
                                   m2="par kg de produit", 
                                   co2sort=co2sort,
                                   sort_type=sort_type,
                                   f1="<",
                                   f2=">",
                                   sur="sur",
                                   lf1="#", 
                                   cf1="nolink", 
                                   lf2=f"/search_ingredients?search={query}&page={page+1}&sort_type={sort_type}", 
                                   cf2="arrow", 
                                   numero=str(page), 
                                   n_total=str(len(data)//nbres+1))
            elif page >= len(data)//nbres+1 :
                return render_template("result_ingredients.html", 
                                   data=data[(len(data)//nbres)*nbres:], search=search, query=query,
                                   produit="Produit",
                                   m1=f"équivalent co2    {triangle}", 
                                   m2="par kg de produit", 
                                   co2sort=co2sort,
                                   sort_type=sort_type,
                                   f1="<",
                                   f2=">",
                                   sur="sur",
                                   lf1=f"/search_ingredients?search={query}&page={page-1}&sort_type={sort_type}", 
                                   cf1="arrow", 
                                   lf2="#", 
                                   cf2="nolink", 
                                   numero=str(len(data)//nbres+1),
                                   n_total=str(len(data)//nbres+1))
            else :
                return render_template("result_ingredients.html", 
                                   data=data[(page-1)*nbres:(page)*nbres], search=search, query=query,
                                   produit="Produit",
                                   m1=f"équivalent co2    {triangle}", 
                                   m2="par kg de produit", 
                                   co2sort=co2sort,
                                   sort_type=sort_type,
                                   f1="<",
                                   f2=">",
                                   sur="sur",
                                   lf1=f"/search_ingredients?search={query}&page={page-1}&sort_type={sort_type}", 
                                   cf1="arrow", 
                                   lf2=f"/search_ingredients?search={query}&page={page+1}&sort_type={sort_type}", 
                                   cf2="arrow", 
                                   numero=str(page), 
                                   n_total=str(len(data)//nbres+1))


@app.route("/search_recipes")
def recipes():
    """
    a page showing a search bar to question the "recipes" db
    """
    nbres = 10  # nombre de resultats affichés sur une seule page
    search = request.args.get("search")
    table = get_recipe_table()
    normalized_query = normalize_str(search)
    codes = table.get(normalized_query, 10)
    data = []
    # on veut maintenant chercher les resultats contenant search
    other = db.session.execute(
                text(f"SELECT name, recipe_uid FROM recipes WHERE normalized_name LIKE '%{normalized_query}%'")
            ).all()
    if codes == [] and other == []:
        if search != "":
            return render_template("no_result_recipes.html", search=search)
        else:
            return render_template("result_recipes.html", data=data, search=search)
    else:
        for code in codes:
            # .all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            recipe = db.session.execute(
                text("SELECT name, recipe_uid FROM recipes WHERE recipe_uid = :c"), {"c": code}
            ).all()[0]
            data.append(recipe)

        if search != "":
            for r in other:
                if r not in data:
                    #data.append(r)
                    data.insert(0, r)
        return render_template("result_recipes.html", data=data[:20], search=search)

@app.route("/account/<string:id>")
def account(id):
    # culivert uid : 6434e9ce-8e46-48a2-9f2f-35699160f526
    username, display_name, bio, creation_date, deletion_date, avatar_uid = db.session.execute(text("SELECT username, display_name, bio, creation_date, deletion_date, avatar_uid FROM users WHERE user_uid = :c"), {"c" : id}).all()[0]
    if deletion_date == None:
        mois = ["janvier",
                "fevrier",
                "mars",
                "avril",
                "mai",
                "juin",
                "juillet",
                "aout",
                "septembre",
                "octobre",
                "novembre",
                "décembre"]
        date_text = f"Utilise CuliVert depuis le {creation_date.day} {mois[creation_date.month-1]} {creation_date.year}"
    else:
        date_text = ""
    return render_template("account.html",
                           username=username,
                           display_name=display_name,
                           bio=bio,
                           date_text=date_text,
                           avatar_uid=get_upload_url(avatar_uid))


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

    # Author
    author = {
        "avatar_url": get_upload_url(recipe.author_account.avatar_uid, "/static/assets/user_avatar_placeholder_from_undraw.svg"),
        "display_name": recipe.author_account.display_name,
        "username": recipe.author_account.username,
        "bio": recipe.author_account.bio,
    }

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
        author=author,
    )
