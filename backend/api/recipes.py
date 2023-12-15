from flask import Blueprint, jsonify
from sqlalchemy import select
#from models.recipe import Ingredient
from models.recipe import Recipe
from db import db
#from search_table import get_recipe_table


# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)



@bp.route("/")
def test():
    """
    test route: return all recipes (json)
    """
    recipes = db.session.query.all()
    recipe_list = [recipe.to_dict() for recipe in recipes]
    return jsonify(recipe_list)


@bp.route("/recipe_info/<uuid:id>")
def recipe_info(id):
    """
    Return the name, the short description and the description of
    the recipe with UUID = id.
    """
    recipe = db.session.get(Recipe, id)
    if recipe is None:
        raise RecipeNotFound(context="Not in DB.", payload={"code": id})
    return jsonify(
        name=recipe.name,
        short_description=recipe.short_description,
        description=recipe.description,
    )


@bp.route("/recipe_ingredients/<uuid:id>")
def recipe_ingredients(id):
    """
    Return the code, the name and the CO2 equivalent of the 
    ingredients from recipe with UUID = id.
    """
    recipe = db.session.get(Recipe, id)
    """
    select ingredient.code, ingredient.name, ingredient.co2 
    from Recipe 
    join IngredientList 
    on Recipe.recipe_uid = IngredientList.recipe_uid
    join Ingredient
    on Ingredient.code = IngredientLink.ingredient_code
    """







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
