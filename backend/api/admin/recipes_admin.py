from flask import Blueprint, jsonify
from sqlalchemy import select, text
from models.recipe import Recipe
from models.ingredient import Ingredient
from models.ingredient_link import IngredientLink
from models.quantity_type import QuantityType
from db import db

# Creates the recipes "router" (aka blueprint in Flask)
bp = Blueprint("recipes", __name__)