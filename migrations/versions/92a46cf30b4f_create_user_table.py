"""create user table

Revision ID: 92a46cf30b4f
Revises: 11f50bd0a676
Create Date: 2023-06-30 13:56:44.704086

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92a46cf30b4f'
down_revision = '11f50bd0a676'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=250), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('crated_at', sa.DateTime(), nullable=True),
    sa.Column('avatar', sa.String(length=255), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.drop_index('ix_contacts_id', table_name='contacts')
    op.create_unique_constraint(None, 'contacts', ['last_name'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='unique')
    op.create_index('ix_contacts_id', 'contacts', ['id'], unique=False)
    op.drop_table('users')
    # ### end Alembic commands ###
