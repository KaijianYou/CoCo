"""empty message

Revision ID: 971f9090f29a
Revises: c08d3488751e
Create Date: 2018-08-05 09:12:17.929424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '971f9090f29a'
down_revision = 'c08d3488751e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article', sa.Column('slug', sa.String(length=16), nullable=False))
    op.create_index(op.f('ix_article_slug'), 'article', ['slug'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_article_slug'), table_name='article')
    op.drop_column('article', 'slug')
    # ### end Alembic commands ###
