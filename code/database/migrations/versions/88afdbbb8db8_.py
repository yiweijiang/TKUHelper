"""empty message

Revision ID: 88afdbbb8db8
Revises: e3f37e75ed3b
Create Date: 2018-02-26 22:29:44.564175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88afdbbb8db8'
down_revision = 'e3f37e75ed3b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Cource_Data', sa.Column('x', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Cource_Data', 'x')
    # ### end Alembic commands ###
