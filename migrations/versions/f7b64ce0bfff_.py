"""empty message

Revision ID: f7b64ce0bfff
Revises: 67f0af76c876
Create Date: 2023-04-29 23:19:59.078682

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7b64ce0bfff'
down_revision = '67f0af76c876'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('delivery',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('item', sa.String(), nullable=True),
    sa.Column('item_category', sa.String(), nullable=True),
    sa.Column('unit', sa.String(), nullable=True),
    sa.Column('pickup', sa.String(), nullable=True),
    sa.Column('pickup_bus_stop', sa.String(), nullable=True),
    sa.Column('delivery', sa.String(), nullable=True),
    sa.Column('delivery_bus_stop', sa.String(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('stage', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('delivery')
    # ### end Alembic commands ###
