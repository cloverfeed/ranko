"""Add User.full_name

Revision ID: 4e474383082f
Revises: 3706a29a80c6
Create Date: 2014-12-18 14:14:25.264445

"""

# revision identifiers, used by Alembic.
revision = '4e474383082f'
down_revision = '3706a29a80c6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('full_name', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'full_name')
    ### end Alembic commands ###
