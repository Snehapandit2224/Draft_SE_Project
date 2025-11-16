"""add indexes to employees table

Revision ID: 9e3dea706739
Revises: e200ccc4b3bc
Create Date: 2025-11-16 13:16:06.452368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e3dea706739'
down_revision: Union[str, Sequence[str], None] = 'e200ccc4b3bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f('ix_employees_department'), 'employees', ['department'], unique=False)
    op.create_index(op.f('ix_employees_position'), 'employees', ['position'], unique=False)
    op.create_index(op.f('ix_employees_status'), 'employees', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_employees_status'), table_name='employees')
    op.drop_index(op.f('ix_employees_position'), table_name='employees')
    op.drop_index(op.f('ix_employees_department'), table_name='employees')
