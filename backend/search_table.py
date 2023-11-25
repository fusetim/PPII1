from collections import Counter
from os.path import exists as path_exists

from db import db
from flask import g
from lsh import (
    TWO_LETTER_SHRINGLES,
    LSHTable,
    generate_permutations,
    load_lsh_table,
    normalize_str,
    shringles,
)
from models.ingredient import Ingredient


def get_ingredient_table():
    """
    Returns the ingredient LSH table.
    """
    if "_ingr_lsht" not in g:
        if False and path_exists("tmp/ingr_lsht.pkl"):
            g._ingr_lsht = load_lsh_table("tmp/ingr_lsht.pkl")
        else:
            ingrs = db.session.execute(db.select(Ingredient)).scalars().all()
            # shr = Counter()
            # for ingr in ingrs:
            #     shr.update(shringles(normalize_str(ingr.name), 2))
            # shr = [ x[0] for x in shr.most_common(500)]
            # shr.sort()
            # print(len(shr))
            shr = TWO_LETTER_SHRINGLES
            g._ingr_lsht = LSHTable(2, 10, generate_permutations(len(shr), 48), shr)
            for ingr in ingrs:
                g._ingr_lsht.insert(normalize_str(ingr.name), ingr.code)
    return g._ingr_lsht


def save_ingredient_table(_err):
    """
    Saves the ingredient LSH table.
    """
    if "_ingr_lsht" in g:
        g._ingr_lsht.save("tmp/ingr_lsht.pkl")