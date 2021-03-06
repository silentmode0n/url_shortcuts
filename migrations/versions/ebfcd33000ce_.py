"""empty message

Revision ID: ebfcd33000ce
Revises: 963341045ea3
Create Date: 2022-05-05 00:29:45.792605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebfcd33000ce'
down_revision = '963341045ea3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shortcuts', sa.Column('visits', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_shortcuts_visits'), 'shortcuts', ['visits'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_shortcuts_visits'), table_name='shortcuts')
    op.drop_column('shortcuts', 'visits')
    # ### end Alembic commands ###
