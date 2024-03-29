"""add: user accounts

Revision ID: 6995c39ff913
Revises: 2ecf1812b293
Create Date: 2023-12-20 13:13:56.306001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6995c39ff913'
down_revision = '2ecf1812b293'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_uid', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=False),
    sa.Column('deletion_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('user_uid'),
    sa.UniqueConstraint('username')
    )
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'users', ['author'], ['user_uid'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    op.drop_table('users')
    # ### end Alembic commands ###
