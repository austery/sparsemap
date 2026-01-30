"""add_title_url_sourcetype_to_analysisresult

Revision ID: 57055332f100
Revises: aedd18522d9b
Create Date: 2026-01-30 17:58:49.710076

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57055332f100'
down_revision: Union[str, Sequence[str], None] = 'aedd18522d9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns with defaults for existing rows
    op.add_column('analysisresult', sa.Column('title', sa.String(), nullable=False, server_default='Untitled'))
    op.add_column('analysisresult', sa.Column('original_url', sa.String(), nullable=True))
    op.add_column('analysisresult', sa.Column('source_type', sa.String(), nullable=False, server_default='text'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('analysisresult', 'source_type')
    op.drop_column('analysisresult', 'original_url')
    op.drop_column('analysisresult', 'title')
