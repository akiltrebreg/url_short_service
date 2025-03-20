"""Add clicks column to shortened_urls

Revision ID: 16e10784f3db
Revises: 2e751387bbf4
Create Date: 2025-03-15 12:39:12.015115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '16e10784f3db'
down_revision: Union[str, None] = '2e751387bbf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shortened_urls', sa.Column('clicks', sa.Integer(), nullable=True))
    op.add_column('shortened_urls', sa.Column('last_accessed_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shortened_urls', 'last_accessed_at')
    op.drop_column('shortened_urls', 'clicks')
    # ### end Alembic commands ###
