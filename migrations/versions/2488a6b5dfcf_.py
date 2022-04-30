"""empty message

Revision ID: 2488a6b5dfcf
Revises: 
Create Date: 2022-02-05 17:45:36.706754

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2488a6b5dfcf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shortcuts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('shortcut_id', sa.String(length=80), nullable=False),
    sa.Column('url', sa.String(length=1000), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('shortcut_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shortcuts')
    # ### end Alembic commands ###
