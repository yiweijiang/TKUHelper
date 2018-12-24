"""empty message

Revision ID: 36497d524c6d
Revises: ee0b47398a60
Create Date: 2018-03-07 15:17:19.277896

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36497d524c6d'
down_revision = 'ee0b47398a60'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('USER_DATA', sa.Column('encrypt', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('USER_DATA', 'encrypt')
    # ### end Alembic commands ###