"""add attrition_alerts table

Revision ID: 29aca3c01fd2
Revises: 37f3c3474a45
Create Date: 2025-11-10 20:15:47.422122

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29aca3c01fd2'
down_revision: Union[str, Sequence[str], None] = '37f3c3474a45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'attrition_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.String(length=64), nullable=True),
        sa.Column('group_name', sa.String(length=64), nullable=True),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('attrition_alerts')
