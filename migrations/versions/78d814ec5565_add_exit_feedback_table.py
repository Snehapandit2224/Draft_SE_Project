"""add exit_feedback table

Revision ID: 78d814ec5565
Revises: 6546b215e2cd
Create Date: 2025-11-10 18:47:35.023938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78d814ec5565'
down_revision: Union[str, Sequence[str], None] = '6546b215e2cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('exit_feedback', schema=None) as batch_op:
        batch_op.alter_column('reason',
               existing_type=sa.Text(),
               type_=sa.Enum('resignation', 'termination', 'retirement', name='exitreason'),
               existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('exit_feedback', schema=None) as batch_op:
        batch_op.alter_column('reason',
               existing_type=sa.Enum('resignation', 'termination', 'retirement', name='exitreason'),
               type_=sa.Text(),
               existing_nullable=True)
