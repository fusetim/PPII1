from db import db
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column


class Ingredient(db.Model):
    """
    Ingredient data model.

    Attributes:
        code: The ingredient unique identifier.
        name: The ingredient name.
        normalized_name: The normalized ingredient name.
        co2: The equivalent Co2 emission per kilogram.
    """
    __tablename__ = "ingredients"
    code: Mapped[str] = mapped_column(String(length=10), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_name: Mapped[str] = mapped_column(Text, nullable=False)
    co2: Mapped[float] = mapped_column(Float, nullable=False)


    def to_dict(self):
        rv = dict()
        rv['type'] = 'ingredient'
        rv['code'] = self.code 
        rv['name'] = self.name 
        rv['eq_co2'] = self.co2
        return rv

