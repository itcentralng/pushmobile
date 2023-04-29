"""empty message

Revision ID: fa19ccadd2fc
Revises: f7b64ce0bfff
Create Date: 2023-04-29 23:41:53.498631

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa19ccadd2fc'
down_revision = 'f7b64ce0bfff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery', schema=None) as batch_op:
        batch_op.add_column(sa.Column('item_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('delivery_phone_number', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('vehicle', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery', schema=None) as batch_op:
        batch_op.drop_column('vehicle')
        batch_op.drop_column('delivery_phone_number')
        batch_op.drop_column('item_type')

    # ### end Alembic commands ###
