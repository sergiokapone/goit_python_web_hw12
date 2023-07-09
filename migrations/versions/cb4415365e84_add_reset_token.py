"""add reset-token

Revision ID: cb4415365e84
Revises: 3c81723c32c5
Create Date: 2023-07-09 17:13:55.890271

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb4415365e84'
down_revision = '3c81723c32c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('reset_token', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'reset_token')
    # ### end Alembic commands ###
