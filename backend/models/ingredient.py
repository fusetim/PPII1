from flask_sqlalchemy.model import Model
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column


class Ingredient(Model):
    """
    Ingredient data model.

    Attributes:
        code: The ingredient unique identifier.
        name: The ingredient name.
        co2: The equivalent Co2 emission per kilogram.
    """

    code: Mapped[str] = mapped_column(String(length=10), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    co2: Mapped[float] = mapped_column(Float)
