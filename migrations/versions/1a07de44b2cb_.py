"""empty message

Revision ID: 1a07de44b2cb
Revises: 8e97205a178a
Create Date: 2018-07-12 16:32:52.060089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a07de44b2cb'
down_revision = '8e97205a178a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article_tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'article_id')
    )
    op.drop_table('article_tags')
    op.add_column('users', sa.Column('nickname', sa.String(length=32), nullable=False))
    op.drop_constraint('users_username_key', 'users', type_='unique')
    op.create_unique_constraint(None, 'users', ['nickname'])
    op.drop_column('users', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('username', sa.VARCHAR(length=32), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'users', type_='unique')
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    op.drop_column('users', 'nickname')
    op.create_table('article_tags',
    sa.Column('tag_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('article_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], name='article_tags_article_id_fkey'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='article_tags_tag_id_fkey'),
    sa.PrimaryKeyConstraint('tag_id', 'article_id', name='article_tags_pkey')
    )
    op.drop_table('article_tag')
    # ### end Alembic commands ###