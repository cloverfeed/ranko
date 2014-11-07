"""Add AudioAnnotation

Revision ID: 51a83463dbb6
Revises: 22608a4a8a06
Create Date: 2014-11-07 13:51:43.097465

"""

# revision identifiers, used by Alembic.
revision = '51a83463dbb6'
down_revision = '22608a4a8a06'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('audio_annotation',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('doc_id', sa.Integer(), nullable=False),
    sa.Column('start', sa.Integer(), nullable=False),
    sa.Column('length', sa.Integer(), nullable=False),
    sa.Column('text', sa.String(), nullable=False),
    sa.Column('state', sa.SmallInteger(), nullable=False),
    sa.ForeignKeyConstraint(['doc_id'], ['document.id'], ),
    sa.ForeignKeyConstraint(['user_id'], [u'user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('audio_annotation')
    ### end Alembic commands ###
