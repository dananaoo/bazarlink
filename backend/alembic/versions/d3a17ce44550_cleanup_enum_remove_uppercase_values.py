"""cleanup_enum_remove_uppercase_values

Revision ID: d3a17ce44550
Revises: e09819f08c2c
Create Date: 2025-11-17 02:22:44.888614

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3a17ce44550'
down_revision: Union[str, None] = 'e09819f08c2c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Remove uppercase enum values, keep only lowercase.
    
    This migration recreates the userrole enum with only lowercase values
    to match the Python code. Since there's no existing data using the
    uppercase values, this is safe to do.
    
    Process:
    1. Create new enum with only lowercase values
    2. Alter users.role column to use new enum
    3. Drop old enum
    4. Rename new enum to 'userrole'
    """
    # Step 1: Create new enum type with only lowercase values
    op.execute("""
        CREATE TYPE userrole_new AS ENUM (
            'consumer',
            'owner',
            'manager',
            'sales_representative'
        )
    """)
    
    # Step 2: Alter the users.role column to use the new enum
    # Cast existing values (if any) to the new enum
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole_new 
        USING role::text::userrole_new
    """)
    
    # Step 3: Drop the old enum type
    op.execute("DROP TYPE userrole")
    
    # Step 4: Rename the new enum to the original name
    op.execute("ALTER TYPE userrole_new RENAME TO userrole")


def downgrade() -> None:
    """Downgrade schema - Restore enum with both uppercase and lowercase values.
    
    Note: This recreates the enum with both cases, but we can't know
    the original order, so this is a best-effort restoration.
    """
    # Create enum with both uppercase and lowercase values
    op.execute("""
        CREATE TYPE userrole_old AS ENUM (
            'CONSUMER',
            'MANAGER',
            'OWNER',
            'SALES_REPRESENTATIVE',
            'consumer',
            'manager',
            'owner',
            'sales_representative'
        )
    """)
    
    # Alter column back
    op.execute("""
        ALTER TABLE users 
        ALTER COLUMN role TYPE userrole_old 
        USING role::text::userrole_old
    """)
    
    # Drop and rename
    op.execute("DROP TYPE userrole")
    op.execute("ALTER TYPE userrole_old RENAME TO userrole")
