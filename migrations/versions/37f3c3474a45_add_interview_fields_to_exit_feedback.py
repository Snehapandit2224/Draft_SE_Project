"""add interview fields to exit_feedback

Revision ID: 37f3c3474a45
Revises: 78d814ec5565
Create Date: 2025-11-10 19:27:29.301916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37f3c3474a45'
down_revision: Union[str, Sequence[str], None] = '78d814ec5565'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('exit_feedback', schema=None) as batch_op:
        batch_op.add_column(sa.Column('interview_completed', sa.Boolean(), nullable=True, default=False))
        batch_op.add_column(sa.Column('interview_date', sa.DateTime(), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('exit_feedback', schema=None) as batch_op:
        batch_op.drop_column('interview_date')
        batch_op.drop_column('interview_completed')
