"""add: user uploads

Revision ID: 2451852c5348
Revises: 256aa48cc78a
Create Date: 2023-12-22 14:54:58.675199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2451852c5348'
down_revision = '256aa48cc78a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_uploads',
    sa.Column('upload_uid', sa.Uuid(), nullable=False),
    sa.Column('author_uid', sa.Uuid(), nullable=False),
    sa.Column('original_filename', sa.Text(), nullable=True),
    sa.Column('content_id', sa.Text(), nullable=False),
    sa.Column('extension', sa.String(length=10), nullable=True),
    sa.Column('upload_date', sa.DateTime(), nullable=False),
    sa.Column('deletion_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['author_uid'], ['users.user_uid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('upload_uid')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_uploads')
    # ### end Alembic commands ###
