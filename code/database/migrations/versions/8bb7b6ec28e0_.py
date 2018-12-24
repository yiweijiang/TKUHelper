"""empty message

Revision ID: 8bb7b6ec28e0
Revises: 3e45b827f042
Create Date: 2018-01-24 17:49:38.522092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bb7b6ec28e0'
down_revision = '3e45b827f042'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Elective_Data',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Student_ID', sa.String(length=64), nullable=True),
    sa.Column('Cource', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Elective_Data')
    # ### end Alembic commands ###