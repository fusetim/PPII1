from flask import Blueprint, jsonify
from sqlalchemy import select, text
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.ingredient_link import IngredientLink
from models.quantity_type import QuantityType
from db import db

# from search_table import get_recipe_table


# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)


@bp.route("/recipes")
def all_recipes():
    """
    test route: return all recipes (json)
    """
    recipes = Recipe.query.all()
    recipe_list = [recipe.to_dict() for recipe in recipes]
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
    """
    Return the name, the short description and the description of
    the recipe with UUID = id.
    """
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
    Return the code, the name and the CO2 equivalent of the
    ingredients from recipe with UUID = id.
    They are formatted as json: ingredients{ingredient{code, name, co2}}
    """

    """
    equivalent to following SQL statement:
    
    SELECT i.code, i.name, i.co2 
    FROM ingredients AS i
    JOIN ingredient_links AS il
    ON i.code = il.ingredient_code
    WHERE il.recipe_uid = id
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
    Return info about the amount of ingredients in
    the recipe with UUID = id, formatted as json:
    ingredient{code, name, co2, quantity, quantity_type}
    with co2 already taking the quantity into account
    and quantity_type = QuantityType.name
    """
    ingredients = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,
            IngredientLink.quantity,
            QuantityType.name,
        )
        .join(IngredientLink, Ingredient.code == IngredientLink.ingredient_code)
        .join(
            QuantityType,
            IngredientLink.quantity_type_uid == QuantityType.quantity_type_uid,
        )
        .filter(IngredientLink.recipe_uid == id)
    )
    ingredients_data = [
        {
            "code": code,
            "name": name,
            "co2": co2_per_quantity * quantity,
            "quantity": quantity,
            "quantity_type": quantity_type,
        }
        for code, name, co2_per_quantity, quantity, quantity_type in ingredients
    ]
    return jsonify(ingredients_data)


@bp.route("recipe_full_data/<uuid:id>")
def recipe_full_data(id):
    """
    Return all the data about the recipe with UUID = id, formatted as json:
    recipe{recipe_uid, name, co2, ingredients[
            ingredient{code, name, co2, quantity, quantity_type}
        ], description}
    """
    ingredients = (
        db.session.query(
            Ingredient.code,
            Ingredient.name,
            Ingredient.co2,
            IngredientLink.quantity,
            QuantityType.name,
        )
        .join(IngredientLink, Ingredient.code == IngredientLink.ingredient_code)
        .join(
            QuantityType,
            IngredientLink.quantity_type_uid == QuantityType.quantity_type_uid,
        )
        .filter(IngredientLink.recipe_uid == id)
    )
    ingredients_data = [
        {"code": code, "name": name, "co2": co2_per_quantity * quantity}
        for code, name, co2_per_quantity, quantity, quantity_type in ingredients
    ]

    # total CO2 amount for the recipe
    recipe_co2 = sum([ing["co2"] for ing in ingredients_data])

    recipe = Recipe.query.get(id)
    recipe_data = {
        "recipe_uid": recipe.recipe_uid,
        "name": recipe.name,
        "co2": recipe_co2,
        "ingredients": ingredients_data,
        "description": recipe.description,
    }
    return jsonify(recipe_data)


class RecipeNotFound(Exception):
    """
    Exception raised when a recipe is not found in the database.
    """

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
