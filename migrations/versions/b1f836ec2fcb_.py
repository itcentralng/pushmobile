"""empty message

Revision ID: b1f836ec2fcb
Revises: 20225170af92
Create Date: 2023-05-12 16:18:28.216381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1f836ec2fcb'
down_revision = '20225170af92'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_name', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('delivery_name', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('delivery', schema=None) as batch_op:
        batch_op.drop_column('delivery_name')
        batch_op.drop_column('customer_name')

    # ### end Alembic commands ###
