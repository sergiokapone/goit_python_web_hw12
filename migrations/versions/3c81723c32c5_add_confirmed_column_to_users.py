"""Add confirmed column to users

Revision ID: 3c81723c32c5
Revises: b69b90d02a35
Create Date: 2023-07-08 18:11:54.907571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c81723c32c5'
down_revision = 'b69b90d02a35'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('contacts_last_name_key', 'contacts', type_='unique')
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    op.create_unique_constraint('contacts_last_name_key', 'contacts', ['last_name'])
    # ### end Alembic commands ###
