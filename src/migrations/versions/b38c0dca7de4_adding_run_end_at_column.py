"""adding run_end_at column

Revision ID: b38c0dca7de4
Revises: 46c2a535e76f
Create Date: 2023-05-31 11:12:09.788256

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils



# revision identifiers, used by Alembic.
revision = 'b38c0dca7de4'
down_revision = '46c2a535e76f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('sync_runs', sa.Column('run_end_at', sa.DateTime(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('sync_runs', 'run_end_at')
    pass
