"""new fields in user model

Revision ID: b13c17ecb9aa
Revises: 95b75622338a
Create Date: 2020-06-08 23:18:20.956130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b13c17ecb9aa'
down_revision = '95b75622338a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('group', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'group')
    # ### end Alembic commands ###
