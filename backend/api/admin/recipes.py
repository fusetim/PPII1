from flask import Blueprint, jsonify, request
from sqlalchemy import select, text
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.ingredient_link import IngredientLink
from models.quantity_type import QuantityType
from db import db
from lsh import normalize_str
from flask_login import current_user
from uuid import uuid4
from api.recipes import RecipeNotFound, not_found
from api.ingredients import IngredientNotFound

# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("admin-recipes", __name__)


@bp.route("/add", methods=["POST"])
def add():
    """
    Add a recipe in the database, provided the input data is valid.
    """
    data = request.get_json()

    name = data.get("title")
    short_description = data.get("short_description")
    description = data.get("description")
    duration = data.get("preparation_time")
    illustration_uid = data.get("illustration_uid")
    ingredients = data.get("ingredients")

    # test to check whether elements that should be non-NULL are actually so
    for element in (
        name,
        short_description,
        description,
        duration,
    ):
        if element is None:
            raise MissingData(context="Missing data to add recipe")

    new_recipe = Recipe(
        recipe_uid=uuid4(),
        name=name,
        normalized_name=normalize_str(name),
        short_description=short_description,
        description=description,
        duration=duration,
        illustration_uid=illustration_uid,
        type="recipe",
        author=current_user.user_uid,
    )
    db.session.add(new_recipe)

    for ing in ingredients:
        ingredient_code = ing["ingr_code"]
        quantity = ing["quantity"]
        quantity_type_uid = ing["quantity_type"]

        # check if the ingredient misses data
        for element in (ingredient_code, quantity, quantity_type_uid):
            if element is None:
                raise MissingData(context="Missing data to add ingredient link")

        # check if the ingredient really exists in the DB
        if Ingredient.query.get(ingredient_code) is None:
            raise IngredientNotFound(
                context="Ingredient is not in the DB.",
                payload={"ingredient_code": ingredient_code},
            )

        link = IngredientLink(
            link_uid=uuid4(),
            recipe_uid=new_recipe.recipe_uid,
            ingredient_code=ingredient_code,
            quantity=quantity,
            quantity_type_uid=quantity_type_uid,
            reference_quantity=ing["reference_quantity"],
            display_name=ing["display_name"],
        )
        db.session.add(link)

    db.session.commit()

    return jsonify({"recipe_uid": new_recipe.recipe_uid})


@bp.route("/edit", methods=["PATCH"])
def edit():
    """
    Edit a recipe from the database.

    Values that can be changed:
    name, short_description, description,duration, illustration.
    If the new value is set to NULL, the previous value will be kept.
    """
    data = request.get_json()

    recipe_uid = data.get("recipe_uid")

    recipe = Recipe.query.get(recipe_uid)
    if recipe is None:
        raise RecipeNotFound(context="Not in DB.", payload={"recipe_uid": recipe_uid})

    fields_to_update = (
        ("name", "title"),
        ("short_description", "short_description"),
        ("description", "description"),
        ("preparation_time", "preparation_time"),
        ("illustration_uid", "illustration_uid")
        # author and type stay the same as before
    )
    for db_field, form_field in fields_to_update:
        new_value = data.get(form_field)
        if new_value is not None:
            setattr(recipe, db_field, new_value)

    recipe.normalized_name = normalize_str(recipe.name)

    new_ingredients = data.get("ingredients")
    if new_ingredients is not None:
        # delete old ingredient links
        old_links = IngredientLink.query.filter(
            IngredientLink.recipe_uid == recipe_uid
        ).all()
        for link in old_links:
            db.session.delete(link)

        # create new links
        for ing in new_ingredients:

            ingredient_code = ing["ingr_code"]
            quantity = ing["quantity"]
            quantity_type_uid = ing["quantity_type"]

            # check if the new ingredient misses data
            for element in (ingredient_code, quantity, quantity_type_uid):
                if element is None:
                    raise MissingData(context="Missing data to add ingredient link")

            # check if the new ingredient really exists in the DB
            if Ingredient.query.get(ingredient_code) is None:
                raise IngredientNotFound(
                    context="Ingredient is not in the DB.",
                    payload={"ingredient_code": ingredient_code},
                )

            link = IngredientLink(
                link_uid=uuid4(),
                recipe_uid=recipe.recipe_uid,
                ingredient_code=ingredient_code,
                quantity=quantity,
                quantity_type_uid=quantity_type_uid,
                reference_quantity=ing["reference_quantity"],
                display_name=ing["display_name"],
            )
            db.session.add(link)

    db.session.commit()

    return jsonify({"recipe_uid": recipe_uid})

@bp.route("/delete/<uuid:id>", methods=["DELETE"])
def delete_recipe(id):
    """
    Delete recipe with uuid = id. Associated ingredient links are also deleted.
    """
    recipe_to_delete = Recipe.query.get(id)
    if recipe_to_delete is None:
        raise RecipeNotFound(context="Not in DB.", payload={"code": id})
    for link in recipe_to_delete.ingredients:
        db.session.delete(link)
    db.session.delete(recipe_to_delete)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify({"error": "Could not delete recipe."}), 500

    return jsonify({"recipe_uid": id})


class MissingData(Exception):
    """Exception raised when some data is missing when trying to create
    or update a recipe.
    """

    status_code = 400

    def __init__(self, context, status_code=None, payload=None):
        super().__init__()
        self.context = context
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["reason"] = "Some data is missing"
        rv["context"] = self.context
        return rv


@bp.errorhandler(MissingData)
def not_found(e):
    """Route handling the MissingData exception."""
    return jsonify(e.to_dict()), e.status_code
