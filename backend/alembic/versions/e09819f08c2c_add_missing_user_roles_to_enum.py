"""Add missing user roles to enum

Revision ID: e09819f08c2c
Revises: 2b22e6f3c9eb
Create Date: 2025-11-17 02:07:16.019838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e09819f08c2c'
down_revision: Union[str, None] = '2b22e6f3c9eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add missing user roles to enum.
    
    This migration adds lowercase enum values to match the Python code.
    Note: The database may also have uppercase values (CONSUMER, OWNER, etc.)
    from earlier table creation. Those are redundant but harmless - the code
    uses lowercase values exclusively via values_callable in the User model.
    """
    # Get connection to check existing values
    conn = op.get_bind()
    
    # Define all required enum values (lowercase - matching Python UserRole enum values)
    required_values = ['consumer', 'owner', 'manager', 'sales_representative']
    
    # Check which values already exist and add missing ones
    for value in required_values:
        # Check if enum value exists
        check_query = sa.text("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_enum 
                WHERE enumlabel = :value 
                AND enumtypid = (
                    SELECT oid 
                    FROM pg_type 
                    WHERE typname = 'userrole'
                )
            )
        """)
        result = conn.execute(check_query, {"value": value})
        exists = result.scalar()
        
        if not exists:
            # Add the enum value
            # Note: In PostgreSQL 9.1+, ALTER TYPE ADD VALUE can be in a transaction
            # but commits immediately. Alembic handles this.
            op.execute(f"ALTER TYPE userrole ADD VALUE '{value}'")


def downgrade() -> None:
    """Downgrade schema - Note: PostgreSQL does not support removing enum values."""
    # PostgreSQL does not support removing enum values directly
    # This would require recreating the enum type, which is complex and risky
    # For safety, we leave the enum values in place
    # If you need to remove them, you would need to:
    # 1. Create a new enum with desired values
    # 2. Alter the column to use the new enum
    # 3. Drop the old enum
    # This is not implemented here for safety reasons
    pass
