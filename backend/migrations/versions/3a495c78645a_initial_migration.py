"""Initial migration.

Revision ID: 3a495c78645a
Revises: 
Create Date: 2023-11-22 07:44:17.455194

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a495c78645a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredients',
    sa.Column('code', sa.VARCHAR(length=10), autoincrement=False, primary_key=True, nullable=True),
    sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('co2', sa.FLOAT, autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ingredients')
    # ### end Alembic commands ###
