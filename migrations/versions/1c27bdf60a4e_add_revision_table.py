"""Add revision table

Revision ID: 1c27bdf60a4e
Revises: 15bf0d6da317
Create Date: 2014-10-29 17:47:54.408270

"""

# revision identifiers, used by Alembic.
revision = '1c27bdf60a4e'
down_revision = '15bf0d6da317'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('revision',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('doc', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['doc'], ['document.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('revision')
    ### end Alembic commands ###
