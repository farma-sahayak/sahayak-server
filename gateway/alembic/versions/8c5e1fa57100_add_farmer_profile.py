"""add farmer profile

Revision ID: 8c5e1fa57100
Revises: 473f4efda169
Create Date: 2025-07-27 02:17:04.451982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c5e1fa57100'
down_revision: Union[str, Sequence[str], None] = '473f4efda169'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('farmer_profiles',
    sa.Column('farmer_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('district', sa.String(length=50), nullable=False),
    sa.Column('state', sa.String(length=50), nullable=False),
    sa.Column('preferred_language', sa.String(length=20), nullable=False),
    sa.Column('primary_crop', sa.ARRAY(sa.String()), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.index'], ),
    sa.PrimaryKeyConstraint('farmer_id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('farmer_profiles')
    # ### end Alembic commands ###
