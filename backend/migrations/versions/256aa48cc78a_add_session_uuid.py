"""add: session UUID

Revision ID: 256aa48cc78a
Revises: 6995c39ff913
Create Date: 2023-12-20 15:37:26.479458

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '256aa48cc78a'
down_revision = '6995c39ff913'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('session_uid', sa.UUID(), nullable=False))
        batch_op.create_unique_constraint(None, ['session_uid'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('session_uid')

    # ### end Alembic commands ###