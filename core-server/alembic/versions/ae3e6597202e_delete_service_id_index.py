"""delete service id index

Revision ID: ae3e6597202e
Revises: f66d6b47566a
Create Date: 2024-10-24 01:09:14.579230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae3e6597202e'
down_revision: Union[str, None] = 'f66d6b47566a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_shared_session_service_id', table_name='shared_session')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_shared_session_service_id', 'shared_session', ['service_id'], unique=False)
    # ### end Alembic commands ###
