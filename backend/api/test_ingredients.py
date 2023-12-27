import pytest
from models.ingredient import Ingredient
from db import db
from app import app


@pytest.fixture()
def client():
    """Returns the Flask test client."""
    return app.test_client()


def test_get_ingredients(client):
    """
    Test the GET /api/ingredients route.

    What is expected to be tested:
    - The route returns a 200 status code if the ingredient exists, or else 404.
    - The route returns a JSON object with the ingredient data if the ingredient exists,
      or else a JSON object with the error message.
    """
    ingredient1 = ["test001", "Beurre doux", "beurre doux", 3.5]
    ingredient2 = ["test002", "Beurre salé", "beurre sale", 3.5]

    with app.app_context():
        if db.session.get(Ingredient, ingredient1[0]) is not None:
            db.session.delete(db.session.get(Ingredient, ingredient1[0]))
        if db.session.get(Ingredient, ingredient2[0]) is not None:
            db.session.delete(db.session.get(Ingredient, ingredient2[0]))
        db.session.add(
            Ingredient(
                code=ingredient1[0],
                name=ingredient1[1],
                normalized_name=ingredient1[2],
                co2=ingredient1[3],
            )
        )
        db.session.add(
            Ingredient(
                code=ingredient2[0],
                name=ingredient2[1],
                normalized_name=ingredient2[2],
                co2=ingredient2[3],
            )
        )
        db.session.commit()

    response = client.get("/api/ingredients/test001")
    assert response.status_code == 200
    assert response.json["code"] == ingredient1[0]
    assert response.json["type"] == "ingredient"
    assert response.json["name"] == ingredient1[1]
    assert response.json["eq_co2"] == ingredient1[3]

    response = client.get("/api/ingredients/test002")
    assert response.status_code == 200
    assert response.json["code"] == ingredient2[0]
    assert response.json["type"] == "ingredient"
    assert response.json["name"] == ingredient2[1]
    assert response.json["eq_co2"] == ingredient2[3]

    response = client.get("/api/ingredients/test003")
    assert response.status_code == 404
    assert (
        response.json["reason"]
        == "Ingredient not found, it might not be in the database, or been deleted."
    )
    assert response.json["code"] == "test003"
    assert response.json["context"] == "Not in DB."

    with app.app_context():
        i1 = db.session.get(Ingredient, ingredient1[0])
        i2 = db.session.get(Ingredient, ingredient2[0])
        db.session.delete(i1)
        db.session.delete(i2)
        db.session.commit()


def test_search_ingredients(client):
    """
    Test the GET /api/ingredients/search/<string:query> route.

    What is expected to be tested:
    - The route returns a 200 status code, if the search is successfully executed.
    - The route returns a JSON list with the search results. An empty list if no results.
    - If an ingredient exists in the DB, whose name matches the query (in particular if query is a
      substring of the ingredient name), it should at least return an ingredient. Due to the implementation
      of the search algorithm, it might not return this ingredient.
    """

    ingredient1 = ["test001", "Beurre doux", "beurre doux", 3.5]

    with app.app_context():
        if db.session.get(Ingredient, ingredient1[0]) is not None:
            db.session.delete(db.session.get(Ingredient, ingredient1[0]))
        db.session.add(
            Ingredient(
                code=ingredient1[0],
                name=ingredient1[1],
                normalized_name=ingredient1[2],
                co2=ingredient1[3],
            )
        )
        db.session.commit()

    response = client.get("/api/ingredients/search/beurre")
    assert response.status_code == 200
    assert len(response.json) >= 1
    for res in response.json:
        assert "code" in res
        assert "eq_co2" in res
        assert "name" in res

    response = client.get("/api/ingredients/search/beurre%20doux")
    assert response.status_code == 200
    assert len(response.json) >= 1
    for res in response.json:
        assert "code" in res
        assert "eq_co2" in res
        assert "name" in res

    with app.app_context():
        i1 = db.session.get(Ingredient, ingredient1[0])
        db.session.delete(i1)
        db.session.commit()
