from os.path import exists as path_exists
from db import db
from flask import g
from lsh import (
    TWO_LETTER_SHRINGLES,
    LSHTable,
    generate_permutations,
    load_lsh_table,
)
from models.ingredient import Ingredient
from models.recipe import Recipe


def get_ingredient_table():
    """
    Returns the ingredient LSH table.
    """
    if "_ingr_lsht" not in g:
        if path_exists("tmp/ingr_lsht.pkl"):
            g._ingr_lsht = load_lsh_table("tmp/ingr_lsht.pkl")
        else:
            ingrs = db.session.execute(db.select(Ingredient)).scalars().all()
            g._ingr_lsht = LSHTable(
                2,
                10,
                generate_permutations(len(TWO_LETTER_SHRINGLES), 48),
                TWO_LETTER_SHRINGLES,
            )
            for ingr in ingrs:
                g._ingr_lsht.insert(ingr.normalized_name, ingr.code)
    return g._ingr_lsht


def get_recipe_table():
    """
    Returns the recipe LSH table.
    """
    if "_recipe_lsht" not in g:
        if path_exists("tmp/recipe_lsht.pkl"):
            g._recipe_lsht = load_lsh_table("tmp/recipe_lsht.pkl")
        else:
            recs = db.session.execute(db.select(Recipe)).scalars().all()
            g._recipe_lsht = LSHTable(
                2,
                10,
                generate_permutations(len(TWO_LETTER_SHRINGLES), 48),
                TWO_LETTER_SHRINGLES,
            )
            for r in recs:
                g._recipe_lsht.insert(r.normalized_name, r.recipe_uid)
    return g._recipe_lsht


def save_search_tables(_err):
    """
    Saves the LSH tables.
    """
    if "_ingr_lsht" in g:
        g._ingr_lsht.save("tmp/ingr_lsht.pkl")
    if "_recipe_lsht" in g:
        g._recipe_lsht.save("tmp/recipe_lsht.pkl")
