"""create books table

Revision ID: b2c3d4e5f6a7
Revises: 5fb65073b818
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = '5fb65073b818'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'books',
        sa.Column('isbn13', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('isbn10', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('subtitle', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('authors', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('categories', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('thumbnail', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('published_year', sa.Integer(), nullable=True),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('num_pages', sa.Integer(), nullable=True),
        sa.Column('ratings_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('isbn13'),
    )
    op.create_index(op.f('ix_books_isbn13'), 'books', ['isbn13'], unique=False)
    op.create_index(op.f('ix_books_title'), 'books', ['title'], unique=False)
    op.create_index(op.f('ix_books_authors'), 'books', ['authors'], unique=False)
    op.create_index(op.f('ix_books_categories'), 'books', ['categories'], unique=False)
    op.create_index(
        op.f('ix_books_published_year'), 'books', ['published_year'], unique=False
    )
    op.create_index(
        op.f('ix_books_average_rating'), 'books', ['average_rating'], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_books_average_rating'), table_name='books')
    op.drop_index(op.f('ix_books_published_year'), table_name='books')
    op.drop_index(op.f('ix_books_categories'), table_name='books')
    op.drop_index(op.f('ix_books_authors'), table_name='books')
    op.drop_index(op.f('ix_books_title'), table_name='books')
    op.drop_index(op.f('ix_books_isbn13'), table_name='books')
    op.drop_table('books')
