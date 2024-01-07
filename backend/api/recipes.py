from flask import Blueprint, jsonify, request
from sqlalchemy import select, text
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.ingredient_link import IngredientLink
from models.quantity_type import QuantityType
from models.recipe_tag import RecipeTag, recipe_tag_association
from models.upload import Upload
from db import db
from search_table import get_recipe_table
from lsh import normalize_str
from util.upload_helper import get_upload_url
from flask_login import login_required, current_user
from uuid import UUID
from http import HTTPStatus

# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)


@bp.route("/search/<string:query>")
def search_recipe(query):
    """Search for a recipe based on a query string."""
    table = get_recipe_table()
    normalized_query = normalize_str(query)
    uids = table.get(normalized_query, 10)
    results = []
    uid_set = set()
    for recipe_uid in uids:
        recipe = db.session.get(Recipe, recipe_uid)
        if recipe is not None:
            data = recipe.to_dict()
            data["origin"] = "lsh-search"
            results.append(data)
            uid_set.add(recipe_uid)
    for recipe in (
        db.session.execute(
            select(Recipe)
            .where(Recipe.normalized_name.like(f"%{normalized_query}%"))
            .limit(min(10, 10 - len(results)))
        )
        .scalars()
        .all()
    ):
        if recipe.recipe_uid not in uid_set:
            data = recipe.to_dict()
            data["origin"] = "db-search"
            results.append(data)
            uid_set.add(recipe.recipe_uid)
    return jsonify(results)


@bp.route("/all")
def all_recipes():
    """
    test route: return all recipes (json)
    """
    recipes = Recipe.query.options().all()
    recipe_list = [ recipe.to_dict() for recipe in recipes ]
    return jsonify(recipe_list)


@bp.route("/all_links")
def all_links():
    """
    test route: return all links (json)
    """
    links = IngredientLink.query.all()
    links_data = [link.to_dict() for link in links]
    return jsonify(links_data)


@bp.route("/all_quantities")
def all_quantities():
    """
    test route: return all quantities (json)
    """
    quantities = QuantityType.query.all()
    quantities_data = [quantity.to_dict() for quantity in quantities]
    return jsonify(quantities_data)


@bp.route("/recipe_info/<uuid:id>")
def recipe_info(id):
    """Return the name, description & short_desc of the recipe with UUID = id."""
    recipe = Recipe.query.get(id)
    if recipe is None:
        raise RecipeNotFound(context="Not in DB.", payload={"recipe_uid": id})
    info = {
        "name": recipe.name,
        "short_description": recipe.short_description,
        "description": recipe.description,
    }
    return jsonify(info)


@bp.route("/recipe_ingredients/<uuid:id>")
def recipe_ingredients(id):
    """
    Return the code, name & CO2 equivalent of the ingredients from recipe
    with UUID = id.

    They are formatted as json: ingredients{ingredient{code, name, co2}}.

    This route might raise a RecipeNotFound exception, if the recipe is not in DB.
    """
    ingredients = (
        db.session.query(Ingredient.code, Ingredient.name, Ingredient.co2)
        .join(IngredientLink, Ingredient.code == IngredientLink.ingredient_code)
        .filter(IngredientLink.recipe_uid == id)
        .all()
    )

    # dictionary list
    ingredients_data = [
        {"code": code, "name": name, "co2": co2} for code, name, co2 in ingredients
    ]

    # If the list is empty we want to check that the requested recipe is in the DB,
    # to properly inform the client that the recipe is not in the DB.
    # Otherwise, we can return an empty list.
    if len(ingredients_data) == 0:
        if db.session.get(Recipe, id) is None:
            raise RecipeNotFound(context="Not in DB.", payload={"recipe_uid": id})

    return jsonify(ingredients_data)


@bp.route("recipe_ingredients_amount/<uuid:id>")
def recipe_ingredients_amount(id):
    """
    Return info about the amount of ingredients in the recipe with UUID = id.

    It is formatted as json:
    ingredient{code, name, co2, quantity, quantity_type_unit, quantity_type_uid}
    with co2 already taking the quantity into account,
    quantity being the value that must be displayed,
    and quantity_type_unit ()= QuantityType.unit) being the unit of quantity.

    This route might raise a RecipeNotFound exception, if the recipe is not in DB.

    eg: "The recipe contains {quantity} {quantity_type_unit} of {name}."
    """
    qry = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,  # per kg
            IngredientLink.quantity,
            IngredientLink.reference_quantity,
            QuantityType.quantity_type_uid,
            QuantityType.unit,
            QuantityType.mass_equivalent,
        )
        .join(IngredientLink, Ingredient.code == IngredientLink.ingredient_code)
        .join(
            QuantityType,
            IngredientLink.quantity_type_uid == QuantityType.quantity_type_uid,
        )
        .filter(IngredientLink.recipe_uid == id)
    )
    ingredients = []
    for (
        code,
        name,
        co2_per_kg,
        quantity,  # in quantity_type
        reference_quantity,  # in kg, can be None
        quantity_type_uid,
        quantity_type_unit,
        mass_equivalent,
    ) in qry:
        if reference_quantity is not None:
            co2 = co2_per_kg * reference_quantity
        else:
            co2 = co2_per_kg * quantity * mass_equivalent

        ingredients.append(
            {
                "code": code,
                "name": name,
                "co2": co2,
                "quantity": quantity,
                "quantity_unit": quantity_type_unit,
                "quantity_type_uid": quantity_type_uid,
            }
        )

    # If the list is empty we want to check that the requested recipe is in the DB,
    # to properly inform the client that the recipe is not in the DB.
    # Otherwise, we can return an empty list.
    if len(ingredients) == 0:
        if db.session.get(Recipe, id) is None:
            raise RecipeNotFound(context="Not in DB.", payload={"recipe_uid": id})

    return jsonify(ingredients)


@bp.route("recipe_full_data/<uuid:id>")
def recipe_full_data(id):
    """
    Return most of the data about the recipe with UUID = id.

    The result is formatted as json:
    recipe{recipe_uid, name, normalized_name, co2, ingredients{...}, description,
        duration, illustration, tags{...}
    }
    ingredient{code, name, co2, quantity, quantity_type_uid, quantity_type_unit}
    tag{recipe_tag_uid, name, normalized_name}

    ingredient[co2] already takes the quantity into account,
    ingredient[quantity] is the value that must be displayed,
    and ingredient[quantity_type_unit] ()= QuantityType.unit) is the quantity unit .

    This route might raise a RecipeNotFound exception, if the recipe is not in DB.
    """
    # Check if the recipe is in the DB
    if db.session.get(Recipe, id) is None:
        raise RecipeNotFound(context="Not in DB.", payload={"recipe_uid": id})

    ing_qry = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,  # per kg
            IngredientLink.quantity,
            IngredientLink.reference_quantity,
            QuantityType.quantity_type_uid,
            QuantityType.unit,
            QuantityType.mass_equivalent,
        )
        .join(IngredientLink, Ingredient.code == IngredientLink.ingredient_code)
        .join(
            QuantityType,
            IngredientLink.quantity_type_uid == QuantityType.quantity_type_uid,
        )
        .filter(IngredientLink.recipe_uid == id)
    )
    ingredients = []
    for (
        code,
        name,
        co2_per_kg,
        quantity,  # in quantity_type
        reference_quantity,  # in kg, can be None
        quantity_type_uid,
        quantity_type_unit,
        mass_equivalent,
    ) in ing_qry:
        if reference_quantity is not None:
            co2 = co2_per_kg * reference_quantity
        else:
            co2 = co2_per_kg * quantity * mass_equivalent

        ingredients.append(
            {
                "code": code,
                "name": name,
                "co2": co2,
                "quantity": quantity,
                "quantity_unit": quantity_type_unit,
                "quantity_type_uid": quantity_type_uid,
            }
        )

    # total CO2 amount for the recipe
    recipe_co2 = sum([ing["co2"] for ing in ingredients])

    # tags of the recipe
    tag_qry = (
        db.session.query(RecipeTag)
        .join(RecipeTag.recipes)
        .filter(Recipe.recipe_uid == id)
        .all()
    )
    tags = [tag.to_dict() for tag in tag_qry]

    recipe = Recipe.query.get(id)
    recipe_data = {
        "recipe_uid": recipe.recipe_uid,
        "name": recipe.name,
        "normalized_name": recipe.normalized_name,
        "co2": recipe_co2,
        "ingredients": ingredients,
        "description": recipe.description,
        "duration": recipe.duration,
        "illustration": get_upload_url(recipe.illustration),
        "tags": tags,
    }
    return jsonify(recipe_data)

@bp.route("/add", methods=["POST"])
@login_required
def add_recipe():
    """
    Add a recipe to the database.
    
    The request is expected to be a json with the following information:
    - title (str): the name of the recipe
    - short_description (str): a short description of the recipe
    - description (str): the steps of the recipe
    - preparation_time (int): the preparation time of the recipe in minutes
    - illustration_uid (UUID|None): the illustration of the recipe
    - ingredients (list): a list of ingredients, each ingredient being a dict with:
        - ingr_code (str): the code of the ingredient
        - display_name (str): the display name of the ingredient
        - quantity (float): the quantity of the ingredient
        - quantity_type (UUID): the quantity type of the ingredient
        - reference_quantity (float|None): the reference quantity of the ingredient in kg
    - tags (list): a list of tags (currently ignored)

    The response is a json with the following information:
    - recipe_uid (UUID): the UUID of the new recipe
    """
    author_uid = current_user.user_uid
    data = request.get_json()
    # Check that the request is valid
    if data is None:
        raise (jsonify({"error": "No json data provided"}), 400)
    if not isinstance(data, dict):
        raise (jsonify({"error": "Invalid json data provided"}), 400)
    if ("title" not in data) or (not isinstance(data["title"], str)):
        raise (jsonify({"error": "Missing title"}), 400)
    if ("short_description" not in data) or (not isinstance(data["short_description"], str)):
        raise (jsonify({"error": "Missing short_description"}), 400)
    if ("preparation_time" not in data) or (not isinstance(data["preparation_time"], int)):
        raise (jsonify({"error": "Missing preparation_time"}), 400)
    if ("ingredients" not in data) or (not isinstance(data["ingredients"], list)):
        raise (jsonify({"error": "Missing ingredients"}), 400)
    recipe = Recipe(
        name=data["title"],
        normalized_name=normalize_str(data["title"]),
        short_description=data["short_description"],
        duration=float(data["preparation_time"]),
        author=author_uid,
        type = "plat",
    )
    # Description can be omited, set it only if it is provided
    if "description" in data and isinstance(data["description"], str):
        recipe.description = data["description"]
    # Illustration can be omited, set it only if it is provided and a valid upload
    if "illustration_uid" in data and isinstance(data["illustration_uid"], str):
        if db.session.get(Upload, UUID(data["illustration_uid"])) is not None:
            recipe.illustration_uid = UUID(data["illustration_uid"])
        else:
            raise (jsonify({"error": "Invalid illustration_uid - it does not exist"}), 400)
    for ingr in data["ingredients"]:
        if not isinstance(ingr, dict):
            raise (jsonify({"error": "Invalid ingredient"}), 400)
        if ("ingr_code" not in ingr) or (not isinstance(ingr["ingr_code"], str)):
            raise (jsonify({"error": "Missing ingredient ingr_code"}), 400)
        if ("display_name" not in ingr) or (not isinstance(ingr["display_name"], str)):
            raise (jsonify({"error": "Missing ingredient display_name"}), 400)
        if ("quantity" not in ingr) or not (isinstance(ingr["quantity"], float) or isinstance(ingr["quantity"], int)):
            raise (jsonify({"error": "Missing ingredient quantity"}), 400)
        if ("quantity_type" not in ingr) or (not isinstance(ingr["quantity_type"], str)):
            raise (jsonify({"error": "Missing ingredient quantity_type"}), 400)
        if ("reference_quantity" in ingr) and not (isinstance(ingr["reference_quantity"], float) or isinstance(ingr["reference_quantity"], int) or (ingr["reference_quantity"] is None)):
            raise (jsonify({"error": "Invalid ingredient reference_quantity"}), 400)
        if "preparation_time" in ingr and ingr["preparation_time"] < 0:
            raise (jsonify({"error": "Negative preparation_time is invalid"}), 400)
        if "quantity" in ingr and ingr["quantity"] < 0:
            raise (jsonify({"error": "Negative quantity is invalid"}), 400)
        if "reference_quantity" in ingr and ingr["reference_quantity"] is not None and ingr["reference_quantity"] < 0:
            raise (jsonify({"error": "Negative reference_quantity is invalid"}), 400)
        if db.session.get(Ingredient, ingr["ingr_code"]) is None:
            raise (jsonify({"error": "Invalid ingredient code"}), 400)
        if db.session.get(QuantityType, UUID(ingr["quantity_type"])) is None:
            raise (jsonify({"error": "Invalid ingredient quantity_type"}), 400)
        recipe.ingredients.append(
            IngredientLink(
                ingredient_code=ingr["ingr_code"],
                quantity=ingr["quantity"],
                display_name=ingr["display_name"],
                quantity_type_uid=UUID(ingr["quantity_type"]),
                reference_quantity=ingr["reference_quantity"] if "reference_quantity" in ingr else None,
            )
        )
    try:
        db.session.add(recipe)
        db.session.commit()
    except:
        db.session.rollback()
        raise (jsonify({"error": "Error while adding recipe to database"}), 500)
    
    return jsonify({"recipe_uid": recipe.recipe_uid}), HTTPStatus.CREATED.value


@bp.route("/edit", methods=["POST", "PATCH"])
@login_required
def edit_recipe():
    """
    Edit a recipe in the database. The author of the recipe must be the current user.
    
    The request is expected to be a json with the following information:
    - recipe_uid (UUID): the UUID of the recipe to edit.
    - title (str): the name of the recipe
    - short_description (str): a short description of the recipe
    - description (str): the steps of the recipe
    - preparation_time (int): the preparation time of the recipe in minutes
    - illustration_uid (UUID|None): the illustration of the recipe
    - ingredients (list): a list of ingredients, each ingredient being a dict with:
        - ingr_code (str): the code of the ingredient
        - display_name (str): the display name of the ingredient
        - quantity (float): the quantity of the ingredient
        - quantity_type (UUID): the quantity type of the ingredient
        - reference_quantity (float|None): the reference quantity of the ingredient in kg
    - tags (list): a list of tags (currently ignored)

    The response is a json with the following information:
    - recipe_uid (UUID): the UUID of the new recipe
    """
    author_uid = current_user.user_uid
    data = request.get_json()
    # Check that the request is valid
    if data is None:
        raise (jsonify({"error": "No json data provided"}), 400)
    if not isinstance(data, dict):
        raise (jsonify({"error": "Invalid json data provided"}), 400)
    if ("recipe_uid" not in data) or (not isinstance(data["recipe_uid"], str)):
        raise (jsonify({"error": "Missing recipe_uid"}), 400)
    recipe = db.session.get(Recipe, UUID(data["recipe_uid"]))

    # Check that the recipe exists and that the user is the author
    if recipe is None:
        raise (jsonify({"error": "Invalid recipe_uid - it does not exist"}), 400)
    if recipe.author != author_uid:
        raise (jsonify({"error": "You are not the author of this recipe"}), 403)
    
    # Update the recipe fields
    if ("title" in data) and isinstance(data["title"], str):
        recipe.name = data["title"]
        recipe.normalized_name = normalize_str(data["title"])
    if ("short_description" in data) and isinstance(data["short_description"], str):
        recipe.short_description = data["short_description"]
    if ("preparation_time" in data) and (isinstance(data["preparation_time"], int) or isinstance(data["preparation_time"], float)):
        recipe.duration = float(data["preparation_time"])
    if ("description" in data) and isinstance(data["description"], str):
        recipe.description = data["description"]
    if "illustration_uid" in data and isinstance(data["illustration_uid"], str):
        if db.session.get(Upload, UUID(data["illustration_uid"])) is not None:
            recipe.illustration_uid = UUID(data["illustration_uid"])
        else:
            raise (jsonify({"error": "Invalid illustration_uid - it does not exist"}), 400)
    for links in recipe.ingredients:
        db.session.delete(links)
    for ingr in data["ingredients"]:
        if not isinstance(ingr, dict):
            raise (jsonify({"error": "Invalid ingredient"}), 400)
        if ("ingr_code" not in ingr) or (not isinstance(ingr["ingr_code"], str)):
            raise (jsonify({"error": "Missing ingredient ingr_code"}), 400)
        if ("display_name" not in ingr) or (not isinstance(ingr["display_name"], str)):
            raise (jsonify({"error": "Missing ingredient display_name"}), 400)
        if ("quantity" not in ingr) or not (isinstance(ingr["quantity"], float) or isinstance(ingr["quantity"], int)):
            raise (jsonify({"error": "Missing ingredient quantity"}), 400)
        if ("quantity_type" not in ingr) or (not isinstance(ingr["quantity_type"], str)):
            raise (jsonify({"error": "Missing ingredient quantity_type"}), 400)
        if ("reference_quantity" in ingr) and not (isinstance(ingr["reference_quantity"], float) or isinstance(ingr["reference_quantity"], int) or (ingr["reference_quantity"] is None)):
            raise (jsonify({"error": "Invalid ingredient reference_quantity"}), 400)
        if "preparation_time" in ingr and ingr["preparation_time"] < 0:
            raise (jsonify({"error": "Negative preparation_time is invalid"}), 400)
        if "quantity" in ingr and ingr["quantity"] < 0:
            raise (jsonify({"error": "Negative quantity is invalid"}), 400)
        if "reference_quantity" in ingr and ingr["reference_quantity"] is not None and ingr["reference_quantity"] < 0:
            raise (jsonify({"error": "Negative reference_quantity is invalid"}), 400)
        if db.session.get(Ingredient, ingr["ingr_code"]) is None:
            raise (jsonify({"error": "Invalid ingredient code"}), 400)
        if db.session.get(QuantityType, UUID(ingr["quantity_type"])) is None:
            raise (jsonify({"error": "Invalid ingredient quantity_type"}), 400)
        recipe.ingredients.append(
            IngredientLink(
                ingredient_code=ingr["ingr_code"],
                quantity=ingr["quantity"],
                display_name=ingr["display_name"],
                quantity_type_uid=UUID(ingr["quantity_type"]),
                reference_quantity=ingr["reference_quantity"] if "reference_quantity" in ingr else None,
            )
        )
    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise (jsonify({"error": "Error while saving the recipe to database"}), 500)
    
    return jsonify({"recipe_uid": recipe.recipe_uid}), HTTPStatus.ACCEPTED.value

@bp.route("/delete", methods=["POST", "DELETE"])
@login_required
def delete_recipe():
    """
    Delete a recipe from the database. The author of the recipe must be the current user.

    The request is expected to be a json with the following information:
    - recipe_uid (UUID): the UUID of the recipe to delete.

    The response is a json with the following information:
    - recipe_uid (UUID): the UUID of the deleted recipe
    
    The response code is:
    - 202 (ACCEPTED) if the recipe was deleted,
    - 400 (BAD REQUEST) if the recipe_uid is invalid,
    - 403 (FORBIDDEN) if the user is not the author of the recipe,
    - 500 (INTERNAL_SERVER_ERROR) if an error occured while deleting the recipe.

    Curl example:
    ```
    curl -X DELETE -H "Content-Type: application/json" -H "Cookie: session" -d '{"recipe_uid": "00000000-0000-0000-0000-000000000000"}' http://localhost:5000/api/recipes/delete
    ```
    """
    author_uid = current_user.user_uid
    
    data = request.get_json()
    # Check that the request is valid
    if data is None:
        raise (jsonify({"error": "No json data provided"}), 400)
    if not isinstance(data, dict):
        raise (jsonify({"error": "Invalid json data provided"}), 400)
    if ("recipe_uid" not in data) or (not isinstance(data["recipe_uid"], str)):
        raise (jsonify({"error": "Missing recipe_uid"}), 400)

    recipe_uid = UUID(data["recipe_uid"])
    recipe = db.session.get(Recipe, recipe_uid)

    # Check that the recipe exists and that the user is the author
    if recipe is None:
        raise (jsonify({"error": "Invalid recipe_uid - it does not exist"}), 400)
    if recipe.author != author_uid:
        raise (jsonify({"error": "You are not the author of this recipe"}), 403)
    
    # Delete the recipe
    try:
        for links in recipe.ingredients:
            db.session.delete(links)
        db.session.delete(recipe)
        db.session.commit()
    except:
        db.session.rollback()
        raise (jsonify({"error": "Error while deleting recipe from database"}), 500)
    
    return jsonify({"recipe_uid": recipe.recipe_uid}), HTTPStatus.ACCEPTED.value

class RecipeNotFound(Exception):
    """Exception raised when a recipe is not found in the database."""

    status_code = 404

    def __init__(self, context, status_code=None, payload=None):
        super().__init__()
        self.context = context
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv[
            "reason"
        ] = "Recipe not found, it might not be in the database, or have been deleted."
        rv["context"] = self.context
        return rv


@bp.errorhandler(RecipeNotFound)
def not_found(e):
    """Route handling the RecipeNotFound exception."""
    return jsonify(e.to_dict()), e.status_code
