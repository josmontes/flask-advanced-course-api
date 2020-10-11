"""empty message

Revision ID: 620a5757a9e0
Revises: 
Create Date: 2020-10-11 12:22:34.694325

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '620a5757a9e0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_users')),
    sa.UniqueConstraint('email', name=op.f('uq_users_email'))
    )
    op.create_foreign_key(op.f('fk_confirmations_user_id_users'), 'confirmations', 'users', ['user_id'], ['id'])
    op.create_unique_constraint(op.f('uq_items_name'), 'items', ['name'])
    op.drop_constraint('items_name_key', 'items', type_='unique')
    op.create_unique_constraint(op.f('uq_stores_name'), 'stores', ['name'])
    op.drop_constraint('stores_name_key', 'stores', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('stores_name_key', 'stores', ['name'])
    op.drop_constraint(op.f('uq_stores_name'), 'stores', type_='unique')
    op.create_unique_constraint('items_name_key', 'items', ['name'])
    op.drop_constraint(op.f('uq_items_name'), 'items', type_='unique')
    op.drop_constraint(op.f('fk_confirmations_user_id_users'), 'confirmations', type_='foreignkey')
    op.drop_table('users')
    # ### end Alembic commands ###