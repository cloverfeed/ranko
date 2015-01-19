"""Drop UNIQUE constraint on User.name

Revision ID: 35c268df8faf
Revises: 35e1dcbfdf30
Create Date: 2015-01-19 18:38:35.069441

"""

# revision identifiers, used by Alembic.
revision = '35c268df8faf'
down_revision = '35e1dcbfdf30'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("user_name_key", "user")


def downgrade():
    op.create_unique_constraint("user_name_key", "user", ["name"])
