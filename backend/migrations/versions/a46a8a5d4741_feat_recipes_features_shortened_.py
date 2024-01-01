"""feat: recipes features shortened ingredient name, illustation and duration

Revision ID: a46a8a5d4741
Revises: ab96f866fd19
Create Date: 2023-12-16 10:51:26.729149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a46a8a5d4741'
down_revision = 'ab96f866fd19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ingredient_links', schema=None) as batch_op:
        batch_op.add_column(sa.Column('display_name', sa.Text(), nullable=True))
        batch_op.create_foreign_key(None, 'recipes', ['recipe_uid'], ['recipe_uid'])
        batch_op.create_foreign_key(None, 'ingredients', ['ingredient_code'], ['code'])

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('normalized_name',
               existing_type=sa.TEXT(),
               nullable=False)
        batch_op.alter_column('co2',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)

    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('duration', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('illustration', sa.Text(), nullable=False))
        batch_op.alter_column('normalized_name',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.alter_column('normalized_name',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.drop_column('illustration')
        batch_op.drop_column('duration')

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('co2',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
        batch_op.alter_column('normalized_name',
               existing_type=sa.TEXT(),
               nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.TEXT(),
               nullable=True)

    with op.batch_alter_table('ingredient_links', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('display_name')

    # ### end Alembic commands ###
