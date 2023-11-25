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
import unicodedata
from unidecode import unidecode


def normalize_str(word: str) -> str:
    """
    Normalizse a string to a lowercase ASCII-only (using unicode transformations) string

    Args:
        - word (str): the string to normalize

    Return:
        A normalize string (lowercase ASCII-only)
    """
    # Normalize the unicode string to the NFKC form (decompose and recompose
    # every char in mostly an unique form)
    un = unicodedata.normalize("NFKC", word)
    # Try to transliterate all unicode characters into an ascii-only form.
    ud = unidecode(un)
    # Finally ignore all unicode and make every char lowercase.
    return ud.encode("ascii", "ignore").decode("ascii").lower()


def get_ingredient_table():
    """
    Returns the ingredient LSH table.
    """
    if "_ingr_lsht" not in g:
        if False and path_exists("tmp/ingr_lsht.pkl"):
            g._ingr_lsht = load_lsh_table("tmp/ingr_lsht.pkl")
        else:
            ingrs = db.session.execute(db.select(Ingredient)).scalars().all()
            shr = TWO_LETTER_SHRINGLES
            g._ingr_lsht = LSHTable(2, 10, generate_permutations(len(shr), 48), shr)
            for ingr in ingrs:
                g._ingr_lsht.insert(ingr.normalized_name, ingr.code)
    return g._ingr_lsht


def get_recipe_table():
    """
    Returns the recipe LSH table.
    """
    if "_recipe_lsht" not in g:
        if False and path_exists("tmp/recipe_lsht.pkl"):
            g._recipe_lsht = load_lsh_table("tmp/recipe_lsht.pkl")
        else:
            recs = db.session.execute(db.select(Recipe)).scalars().all()
            shr = TWO_LETTER_SHRINGLES
            g._recipe_lsht = LSHTable(2, 10, generate_permutations(len(shr), 48), shr)
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