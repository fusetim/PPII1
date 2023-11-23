from db import db
from sqlalchemy import String, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid

class QuantityType(db.Model):
    """
    QuantityType data model.
    Modelize a type of quantity (mass, volume, etc.) and how to convert it to a mass equivalent (in kg).

    Attributes:
        quantity_type_uid: The quantity type unique identifier.
        name: The quantity type name.
        localized_key: The key used to localize the quantity type name.
        mass_equivalent: The mass equivalent per unit of the quantity type (in kg).
    """
    __tablename__ = "quantity_types"
    quantity_type_uid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    localized_key: Mapped[str] = mapped_column(String(length=100), nullable=True)
    mass_equivalent: Mapped[float] = mapped_column(Float, nullable=False)