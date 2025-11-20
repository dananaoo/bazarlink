"""move_delivery_options_to_supplier

Revision ID: 1b4f8ca0e372
Revises: 87a7758524c0
Create Date: 2025-11-21 00:46:08.982449

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1b4f8ca0e372'
down_revision: Union[str, None] = '87a7758524c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Move delivery options from products to suppliers.
    
    - Removes delivery_available and pickup_available from products
    - Adds delivery_available, pickup_available, and lead_time_days to suppliers
    - Sets default values (True, True, 1) for existing suppliers using server_default
    """
    # Step 1: Remove delivery options from products
    op.drop_column('products', 'pickup_available')
    op.drop_column('products', 'delivery_available')
    
    # Step 2: Add delivery options to suppliers with server defaults
    # This ensures existing suppliers get default values automatically
    op.add_column('suppliers', sa.Column('delivery_available', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('suppliers', sa.Column('pickup_available', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('suppliers', sa.Column('lead_time_days', sa.Integer(), nullable=True, server_default='1'))
    
    # Step 3: Update existing suppliers to have default values (safety measure)
    # This ensures all existing records have values even if server_default didn't apply
    op.execute("""
        UPDATE suppliers 
        SET delivery_available = COALESCE(delivery_available, true),
            pickup_available = COALESCE(pickup_available, true),
            lead_time_days = COALESCE(lead_time_days, 1)
        WHERE delivery_available IS NULL 
           OR pickup_available IS NULL 
           OR lead_time_days IS NULL
    """)


def downgrade() -> None:
    """Downgrade schema - Move delivery options back from suppliers to products."""
    # Step 1: Remove delivery options from suppliers
    op.drop_column('suppliers', 'lead_time_days')
    op.drop_column('suppliers', 'pickup_available')
    op.drop_column('suppliers', 'delivery_available')
    
    # Step 2: Add delivery options back to products
    op.add_column('products', sa.Column('delivery_available', sa.BOOLEAN(), autoincrement=False, nullable=True, server_default='true'))
    op.add_column('products', sa.Column('pickup_available', sa.BOOLEAN(), autoincrement=False, nullable=True, server_default='true'))
