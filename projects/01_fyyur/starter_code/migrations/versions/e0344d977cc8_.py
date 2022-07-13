"""empty message

Revision ID: e0344d977cc8
Revises: 94fec836611d
Create Date: 2022-06-04 18:03:42.599735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0344d977cc8'
down_revision = '94fec836611d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('show_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'venue', 'show', ['show_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'venue', type_='foreignkey')
    op.drop_column('venue', 'show_id')
    # ### end Alembic commands ###