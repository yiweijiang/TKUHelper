"""empty message

Revision ID: b0540f6cac85
Revises: 6453205b32d1
Create Date: 2018-03-02 16:39:42.215659

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0540f6cac85'
down_revision = '6453205b32d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Cource_Data', 'Cource_Week')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Cource_Data', sa.Column('Cource_Week', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
