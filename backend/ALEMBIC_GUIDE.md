# Alembic Migration Guide

This guide explains how to use Alembic for database migrations in the Supplier Consumer Platform.

## Overview

Alembic is a database migration tool for SQLAlchemy. It allows you to:
- Track database schema changes
- Apply migrations in a controlled way
- Rollback changes if needed
- Keep database schema in sync across environments

## Initial Setup

Alembic has been initialized and configured. The initial migration has been created and marked as applied (since tables already existed).

## Configuration

- **alembic.ini**: Main Alembic configuration file
- **alembic/env.py**: Migration environment script (configured to use app settings)
- **alembic/versions/**: Directory containing migration files

The configuration uses `DATABASE_URL` from `app.core.config.settings`, so it automatically uses the same database connection as the application.

## Common Commands

### Check Current Migration Status

```bash
alembic current
```

Or using Makefile:
```bash
make migrate-current
```

### View Migration History

```bash
alembic history
```

Or using Makefile:
```bash
make migrate-history
```

### Create a New Migration

When you modify models, create a migration:

```bash
alembic revision --autogenerate -m "description of changes"
```

Or using Makefile:
```bash
make migrate-create MESSAGE="add new field to user table"
```

**Important**: Always review the generated migration file before applying it!

### Apply Migrations

Apply all pending migrations:

```bash
alembic upgrade head
```

Or using Makefile:
```bash
make migrate-upgrade
```

### Rollback Migrations

Rollback one migration:

```bash
alembic downgrade -1
```

Or rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

Or using Makefile:
```bash
make migrate-downgrade REVISION="-1"
```

## Workflow

### Adding a New Field to a Model

1. **Modify the model** in `app/models/`:
   ```python
   class User(Base):
       # ... existing fields ...
       new_field = Column(String(100), nullable=True)
   ```

2. **Create a migration**:
   ```bash
   alembic revision --autogenerate -m "add new_field to user"
   ```

3. **Review the migration file** in `alembic/versions/`:
   - Check that the changes are correct
   - Add any data migrations if needed
   - Verify that nullable/default values are appropriate

4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

5. **Test the changes**:
   - Run your application
   - Verify the new field works correctly
   - Run tests

### Modifying an Existing Field

1. **Modify the model**
2. **Create a migration** (same as above)
3. **Review the migration** - Alembic may generate `ALTER COLUMN` statements
4. **Apply the migration**
5. **Test the changes**

### Removing a Field

1. **Remove the field from the model**
2. **Create a migration**
3. **Review the migration** - ensure data loss is acceptable
4. **Apply the migration**

## Best Practices

1. **Always review migrations** before applying them
2. **Test migrations** on a development database first
3. **Never edit applied migrations** - create a new one instead
4. **Use descriptive messages** when creating migrations
5. **Keep migrations small** - one logical change per migration
6. **Backup your database** before applying migrations in production
7. **Run tests** after applying migrations

## Troubleshooting

### Migration conflicts

If you have conflicts (e.g., multiple heads), you can merge them:

```bash
alembic merge -m "merge migrations" <revision1> <revision2>
```

### Database out of sync

If your database is out of sync with migrations:

1. Check current state: `alembic current`
2. Check what migrations exist: `alembic history`
3. If needed, mark the current state: `alembic stamp <revision_id>`

### Autogenerate not detecting changes

- Ensure all models are imported in `alembic/env.py`
- Check that models inherit from `Base`
- Verify that `target_metadata = Base.metadata` is set in `env.py`

## Migration File Structure

Each migration file contains:

- **revision**: Unique identifier for the migration
- **down_revision**: Previous migration (creates a chain)
- **upgrade()**: Function that applies the migration
- **downgrade()**: Function that rolls back the migration

Example:
```python
def upgrade() -> None:
    op.add_column('users', sa.Column('new_field', sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column('users', 'new_field')
```

## Production Considerations

1. **Always backup** before applying migrations
2. **Test migrations** in staging first
3. **Plan for downtime** if migrations are large
4. **Monitor** the migration process
5. **Have a rollback plan** ready

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

