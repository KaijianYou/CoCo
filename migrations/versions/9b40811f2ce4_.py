"""empty message

Revision ID: 9b40811f2ce4
Revises: 1a07de44b2cb
Create Date: 2018-07-12 17:44:32.513571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b40811f2ce4'
down_revision = '1a07de44b2cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article_tag', sa.Column('id', sa.Integer(), nullable=False))
    op.add_column('article_tag', sa.Column('is_enable', sa.Boolean(), nullable=True))
    op.add_column('article_tag', sa.Column('utc_created', sa.DateTime(), nullable=True))
    op.add_column('article_tag', sa.Column('utc_updated', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('article_tag', 'utc_updated')
    op.drop_column('article_tag', 'utc_created')
    op.drop_column('article_tag', 'is_enable')
    op.drop_column('article_tag', 'id')
    # ### end Alembic commands ###