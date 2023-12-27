from flask import Blueprint, jsonify
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


@bp.route("/recipes")
def all_recipes():
    """
    test route: return all recipes (json)
    """
    recipes = Recipe.query.options().all()
    recipe_list = [
        {
            "type": "recipe",
            "recipe_uid": recipe.recipe_uid,
            "name": recipe.name,
            "short_description": recipe.short_description,
            "description": recipe.description,
            "type": recipe.type,
            "author": recipe.author,
            "duration": recipe.duration,
            # broken for some reason:
            # "illustration": recipe.illustration,
        }
        for recipe in recipes
    ]
    return jsonify(recipe_list)


@bp.route("/links")
def all_links():
    """
    test route: return all links (json)
    """
    links = IngredientLink.query.all()
    links_data = [link.to_dict() for link in links]
    return jsonify(links_data)


@bp.route("/quantities")
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
        raise RecipeNotFound(context="Not in DB.", payload={"code": id})
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

    They are formatted as json: ingredients{ingredient{code, name, co2}}
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
    return jsonify(ingredients_data)


@bp.route("recipe_ingredients_amount/<uuid:id>")
def recipe_ingredients_amount(id):
    """
    Return info about the amount of ingredients in the recipe with UUID = id.

    It is formatted as json:
    ingredient{code, name, co2, quantity, quantity_type}
    with co2 already taking the quantity into account,
    quantity being the value that must be displayed,
    and quantity_type ()= QuantityType.name) being the unit of quantity.

    eg: "The recipe contains {quantity} {quantity_type} of {name}."
    """
    qry = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,  # per kg
            IngredientLink.quantity,
            IngredientLink.reference_quantity,
            QuantityType.name,
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
        quantity_type,
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
                "quantity_type": quantity_type,
            }
        )
    return jsonify(ingredients)


@bp.route("recipe_full_data/<uuid:id>")
def recipe_full_data(id):
    """
    Return most of the data about the recipe with UUID = id.

    The result is formatted as json:
    recipe{recipe_uid, name, normalized_name, co2, ingredients{...}, description,
        duration, illustration, tags{...}
    }
    ingredient{code, name, co2, quantity, quantity_type}
    tag{recipe_tag_uid, name, normalized_name}

    ingredient[co2] already takes the quantity into account,
    ingredient[quantity] is the value that must be displayed,
    and ingredient[quantity_type] ()= QuantityType.name) is the quantity unit .
    """

    ing_qry = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,  # per kg
            IngredientLink.quantity,
            IngredientLink.reference_quantity,
            QuantityType.name,
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
        quantity_type,
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
                "quantity_type": quantity_type,
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
        # broken for some reason
        # "illustration": recipe.illustration,
        "tags": tags,
    }
    return jsonify(recipe_data)


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
