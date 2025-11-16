"""add role to user model

Revision ID: b6e168eac840
Revises: 9e3dea706739
Create Date: 2025-11-16 13:35:50.684974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6e168eac840'
down_revision: Union[str, Sequence[str], None] = '9e3dea706739'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('role', sa.String(length=64), nullable=True, server_default='employee'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'role')
