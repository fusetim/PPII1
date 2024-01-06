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
from math import ceil
from md_render import markdown_render
from util.human_format import format_duration, format_mass
from util.upload_helper import get_upload_url
from login import login_manager
from flask_login import login_required, current_user
from http import HTTPStatus

# Add the root directory to the PYTHONPATH
p = os.path.abspath(".")
sys.path.insert(1, p)

# Entrypoint for the Flask app.
app = Flask(__name__)
# Register the `/api` & views routes
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(views, url_prefix="/")
# Load the config
if os.path.exists("config.toml"):
    app.config.from_file("config.toml", load=tomllib.load, text=False)
else:
    app.config.from_prefixed_env()
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

# Setup the error handlers
HANDLED_ERRORS = [
    (400, "Mauvaise Requête", ["La syntaxe de la requête est invalide.", "Veuillez contacter un administrateur si l'erreur se reproduit."]),
    (401, "Non-Autorisé", ["Une authentification est requise pour poursuivre la requête.", "Veuillez vous connecter puis réessayer."]),
    (403, "Interdit", ["L'accès à ce contenu est restreint.", "Il est peut-être nécessaire de se connecter avant de réessayer."]),
    (404, "Introuvable", ["La page que vous tentez d'accéder n'existe pas.", "Elle a peut-être été supprimée ou déplacée."]),
    (405, "Méthode Non Autorisée", ["La requête utilise un verbe qui n'est pas pris en charge par le serveur."]),
    (413, "Requêtre Trop Longue", ["La requête est trop longue.", "Si vous essayez d'uploader un fichier, il se peut que vous dépasser la limite définie par le serveur."]),
    (429, "Trop de Requêtes", ["L'utilisateur a dépassé les limites de requêtes acceptables.", "Veuillez patientez quelques minutes avant de réessayer."]),
    (500, "Erreur Interne du Serveur", ["Le serveur a rencontré une situation qu'il ne sait pas traiter."]),
]

def handle_error(status_code, phrase, description):
    """
    Route generator to handle a specific HTTP error.

    Args:
        status_code (int): The HTTP Status code.
        phrase (str): Custom (or not) HTTP Status phrase.
        description (list[str]): A small description to display the user. Each item is a line.

    Returns:
        A route that can handle this particular HTTP error.
    """
    def handle_route(e):
        return render_template("error-page.html", status_code=status_code, phrase=phrase, description=description), status_code
    return handle_route

for (status_code, phrase, description) in HANDLED_ERRORS:
    app.register_error_handler(status_code, handle_error(status_code, phrase, description))


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
    # nbres : nb de resultats affichés sur une meme page
    nbres = 10
    search = request.args.get("search")
    table = get_ingredient_table()
    normalized_query = normalize_str(search)
    codes = table.get(normalized_query)
    data = []
    other = db.session.execute(
        text(
            f"SELECT name, co2 FROM ingredients WHERE normalized_name LIKE '%{normalized_query}%'"
        )
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
                    # data.append(r)
                    data.insert(0, r)
        sort_type = request.args.get("sort_type")
        if sort_type in (None, ""):
            sort_type = 0
        else:
            sort_type = int(sort_type)

        # on trie data comme voulu (0 : par nom ; 1 par co2 croissant ; 2 par co2 decroissant)
        if sort_type == 0:
            data.sort(key=lambda a: a[0])
            co2sort = 2
            triangle = ""
        elif sort_type == 1:
            data.sort(key=lambda a: a[1], reverse=False)
            co2sort = 2
            triangle = "▲"
        else:
            data.sort(key=lambda a: a[1], reverse=True)
            co2sort = 1
            triangle = "▼"

        if len(data) <= nbres:
            return render_template(
                "result_ingredients.html",
                data=data,
                search=search,
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
                n_total="1",
            )
        else:
            page = request.args.get("page")
            if page == None:
                page = 1
            else:
                page = int(page)

            # on recrée le format mot1+mo2+... pour ne pas que au passage d'une page à l'autre
            # on ne garde que le premier mot de la recherche (pour qu'il n'y ait pas d'espace dans l'url)
            query = ""
            for c in search:
                if c == " ":
                    query += "+"
                else:
                    query += c
            if page <= 1:
                # première page
                return render_template(
                    "result_ingredients.html",
                    data=data[:nbres],
                    search=search,
                    query=query,
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
                    numero="1",
                    n_total=str(ceil(len(data) / nbres)),
                )
            # dernière page
            elif page >= ceil(len(data) / nbres):
                return render_template(
                    "result_ingredients.html",
                    data=data[ceil(len(data) / nbres - 1) * nbres :],
                    search=search,
                    query=query,
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
                    numero=str(ceil(len(data) / nbres)),
                    n_total=str(ceil(len(data) / nbres)),
                )
            # les autres pages au milieu
            else:
                return render_template(
                    "result_ingredients.html",
                    data=data[(page - 1) * nbres : (page) * nbres],
                    search=search,
                    query=query,
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
                    n_total=str(ceil(len(data) / nbres)),
                )


@app.route("/search_recipes")
def recipes():
    """
    a page showing a search bar to question the "recipes" db
    """
    nbres = 10  # nombre de resultats affichés sur une seule page

    search = request.args.get("search")
    table = get_recipe_table()
    normalized_query = normalize_str(search)
    codes = table.get(normalized_query)
    data = []
    # on veut maintenant chercher les resultats contenant search
    other = db.session.execute(
        text(
            f"SELECT name, recipe_uid, author FROM recipes WHERE normalized_name LIKE '%{normalized_query}%'"
        )
    ).all()
    if search == "":
        return render_template("result_recipes.html", data=data, search=search)
    elif codes == [] and other == []:
        return render_template("no_result_recipes.html", search=search)
    else:
        for code in codes:
            # .all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
            recipe = db.session.execute(
                text(
                    f"SELECT name, recipe_uid, author FROM recipes WHERE recipe_uid = :c"
                ),
                {"c": code},
            ).all()[0]
            data.append(recipe)

        if search != "":
            for r in other:
                if r not in data:
                    # data.append(r)
                    data.insert(0, r)
        recipes = []

        # on rajoute l'username à data
        for r in data:
            username = db.session.execute(
                text("SELECT username FROM users WHERE user_uid = :c"), {"c": r[2]}
            ).all()[0][0]
            recipes.append((r[0], r[1], username))
        data = recipes
        if len(data) <= nbres:
            return render_template(
                "result_recipes.html",
                data=data,
                search=search,
                f1="<",
                f2=">",
                sur="sur",
                lf1="#",
                cf1="nolink",
                lf2="#",
                cf2="nolink",
                numero="1",
                n_total="1",
            )
        else:
            page = request.args.get("page")
            if page == None:
                page = 1
            else:
                page = int(page)

            # on recrée le format mot1+mo2+... pour ne pas que au passage d'une page à l'autre
            # on ne garde que le premier mot de la recherche (pour qu'il n'y ait pas d'espace dans l'url)
            query = ""
            for c in search:
                if c == " ":
                    query += "+"
                else:
                    query += c
            if page <= 1:
                return render_template(
                    "result_recipes.html",
                    data=data[:nbres],
                    search=search,
                    query=query,
                    f1="<",
                    f2=">",
                    sur="sur",
                    lf1="#",
                    cf1="nolink",
                    lf2=f"/search_recipes?search={query}&page={page+1}",
                    cf2="arrow",
                    numero="1",
                    n_total=str(ceil(len(data) / nbres)),
                )
            elif page >= ceil(len(data) / nbres):
                return render_template(
                    "result_recipes.html",
                    data=data[(ceil(len(data) / nbres - 1)) * nbres :],
                    search=search,
                    query=query,
                    f1="<",
                    f2=">",
                    sur="sur",
                    lf1=f"/search_recipes?search={query}&page={page-1}",
                    cf1="arrow",
                    lf2="#",
                    cf2="nolink",
                    numero=str(ceil(len(data) / nbres)),
                    n_total=str(ceil(len(data) / nbres)),
                )
            else:
                return render_template(
                    "result_recipes.html",
                    data=data[(page - 1) * nbres : (page) * nbres],
                    search=search,
                    query=query,
                    f1="<",
                    f2=">",
                    sur="sur",
                    lf1=f"/search_recipes?search={query}&page={page-1}",
                    cf1="arrow",
                    lf2=f"/search_recipes?search={query}&page={page+1}",
                    cf2="arrow",
                    numero=str(page),
                    n_total=str(ceil(len(data) / nbres)),
                )


@app.route("/accounts/<string:username>")
def account(username):
    """
    a page showing the profile of a user

    Args:
        id (string): the UUID of the user to display
    """
    nbres = 10  # nombre de resultats affichés sur une seule page
    # culivert uid : 6434e9ce-8e46-48a2-9f2f-35699160f526
    # Sacha uid : 6be9e17b-5311-4f8a-b497-c744dd6fe7c4
    (
        user_uid,
        display_name,
        bio,
        creation_date,
        deletion_date,
        avatar_uid,
    ) = db.session.execute(
        text(
            "SELECT user_uid, display_name, bio, creation_date, deletion_date, avatar_uid FROM users WHERE username = :c"
        ),
        {"c": username},
    ).all()[0]
    if deletion_date == None:
        mois = [
            "janvier",
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
            "décembre",
        ]
        date_text = f"Utilise CuliVert depuis le {creation_date.day} {mois[creation_date.month-1]} {creation_date.year}"
    else:
        date_text = ""
    # .all to get the list of sql outputs and [0] to get the tuple str-int (the output is a singleton)
    data = db.session.execute(
        text("SELECT name, recipe_uid FROM recipes WHERE author = :c"), {"c": user_uid}
    ).all()
    if len(data) <= nbres:
        return render_template(
            "account.html",
            username=username,
            display_name=display_name,
            bio=bio,
            date_text=date_text,
            avatar_url=get_upload_url(
                avatar_uid, "/static/assets/user_avatar_placeholder_from_undraw.svg"
            ),
            data=data,
        )
    else:
        page = request.args.get("page")
        if page == None:
            page = 1
        else:
            page = int(page)

        
        # première page
        if page <= 1:
            return render_template(
                "account.html",
                username=username,
                display_name=display_name,
                bio=bio,
                date_text=date_text,
                avatar_uid=get_upload_url(
                    avatar_uid, "/static/assets/user_avatar_placeholder_from_undraw.svg"
                ),
                data=data[:nbres],
                f1="<",
                f2=">",
                sur="sur",
                lf1="#",
                cf1="nolink",
                lf2=f"/accounts/{username}?search={query}&page={page+1}",
                cf2="arrow",
                numero="1",
                n_total=str(ceil(len(data) / nbres)),
            )
        # dernière page
        elif page >= ceil(len(data) / nbres):
            return render_template(
                "account.html",
                username=username,
                display_name=display_name,
                bio=bio,
                date_text=date_text,
                avatar_uid=get_upload_url(
                    avatar_uid, "/static/assets/user_avatar_placeholder_from_undraw.svg"
                ),
                data=data[(ceil(len(data) / nbres - 1)) * nbres :],
                f1="<",
                f2=">",
                sur="sur",
                lf1=f"/accounts/{username}?search={query}&page={page-1}",
                cf1="arrow",
                lf2="#",
                cf2="nolink",
                numero=str(ceil(len(data) / nbres)),
                n_total=str(ceil(len(data) / nbres)),
            )
        # page intermédiaire
        else:
            return render_template(
                "account.html",
                username=username,
                display_name=display_name,
                bio=bio,
                date_text=date_text,
                avatar_uid=get_upload_url(
                    avatar_uid, "/static/assets/user_avatar_placeholder_from_undraw.svg"
                ),
                data=data[(page - 1) * nbres : (page) * nbres],
                f1="<",
                f2=">",
                sur="sur",
                lf1=f"/accounts/{username}?search={query}&page={page-1}",
                cf1="arrow",
                lf2=f"/accounts/{username}?search={query}&page={page+1}",
                cf2="arrow",
                numero=str(page),
                n_total=str(ceil(len(data) / nbres)),
            )


@app.route("/recipe/<uuid:recipe_uid>")
def get_recipe(recipe_uid):
    """
    a page displaying the recipe with the given id

    Args:
        recipe_uid (uuid): the UUID of the recipe to display
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
        return render_template("error-page.html", status_code=404, phrase="Recette introuvable", description=["La recette que vous tentez d'accéder n'existe pas.", "Elle a peut-être été supprimée ou déplacée."]), 404

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
        "avatar_url": get_upload_url(
            recipe.author_account.avatar_uid,
            "/static/assets/user_avatar_placeholder_from_undraw.svg",
        ),
        "display_name": recipe.author_account.display_name,
        "username": recipe.author_account.username,
        "bio": recipe.author_account.bio,
        "uuid": recipe.author_account.user_uid,
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
        is_owner=current_user.is_authenticated and current_user.user_uid == recipe.author,
    )


@app.route("/editor")
@login_required
def editor():
    """
    Editor page, allowing the user to create/edit a recipe.
    """
    if request.args.get("recipe_uid") is not None:
        recipe_uid = request.args.get("recipe_uid")
        recipe = db.session.get(Recipe, recipe_uid)
        if recipe is None:
            return render_template("error-page.html", status_code=404, phrase="Recette introuvable", description=["La recette que vous tentez d'accéder n'existe pas.", "Elle a peut-être été supprimée ou déplacée."]), 404
        else:
            if recipe.author != current_user.user_uid:
                return render_template("error-page.html", status_code=403, phrase="Accès interdit", description=["Vous n'êtes pas autorisé à accéder à cette page.", "Seul l'auteur de la recette peut la modifier."]), 403
            return render_template(
                "editor.html",
                recipe_uid=recipe_uid,
                name=recipe.name,
                preparation_time=recipe.duration,
                tags=[tag.name for tag in recipe.tags],
                short_description=recipe.short_description,
                description=recipe.description,
                ingredients=[
                    {
                        "code": link.ingredient.code,
                        "name": link.ingredient.name,
                        "display_name": link.display_name,
                        "quantity": link.quantity,
                        "quantity_type_uid": link.quantity_type_uid,
                        "unit": link.quantity_type.unit,
                        "reference_quantity": link.reference_quantity,
                    }
                    for link in recipe.ingredients
                ],
            )
    else:
        return render_template(
                "editor.html",
                recipe_uid=None,
                name="",
                preparation_time=30,
                tags=[],
                short_description="",
                description="",
                ingredients=[],
            )