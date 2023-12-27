import pytest
from models.recipe import Recipe
from db import db
from app import app
import uuid


@pytest.fixture()
def client():
    """Returns the Flask test client."""
    return app.test_client()


def test_search_recipe(client):
    """
    Test the GET /api/recipe/search/<string:query> route.

    What is expected to be tested:
    - The route returns a 200 status code, if the search is successfully executed.
    - The route returns a JSON list with the search results. An empty list if no results.
    - If an recipe exists in the DB, whose name matches the query (in particular if query is a
      substring of the recipe name), it should at least return an recipe. Due to the implementation
      of the search algorithm, it might not return this recipe.
    """

    recipe1 = [
        uuid.UUID("18047cd6-adb3-4600-b249-fb8438a9850c"),
        "Pâte à la sauce de test",
        "pate a la sauce de test",
        "short description",
        "description",
        "type",
        uuid.uuid4(),
    ]

    with app.app_context():
        if db.session.get(Recipe, recipe1[0]) is not None:
            db.session.delete(db.session.get(Recipe, recipe1[0]))
        db.session.add(
            Recipe(
                recipe_uid=recipe1[0],
                name=recipe1[1],
                normalized_name=recipe1[2],
                short_description=recipe1[3],
                description=recipe1[4],
                type=recipe1[5],
                author=recipe1[6],
            )
        )
        db.session.commit()

    response = client.get("/api/recipes/search/pate")
    assert response.status_code == 200
    assert len(response.json) >= 1
    for res in response.json:
        assert "recipe_uid" in res
        assert "name" in res
        assert "short_description"
        assert "author" in res
        assert "type" in res

    response = client.get("/api/recipes/search/pate%20a%20la%20sauce%20de%20test")
    assert response.status_code == 200
    assert len(response.json) >= 1
    for res in response.json:
        assert "recipe_uid" in res
        assert "name" in res
        assert "short_description"
        assert "author" in res
        assert "type" in res

    with app.app_context():
        r1 = db.session.get(Recipe, recipe1[0])
        db.session.delete(r1)
        db.session.commit()
