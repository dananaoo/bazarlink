# Data Archival Guide

## Overview

The system implements a data retention and archival policy using a separate PostgreSQL schema called `archive`. This allows for compliance with data retention requirements while keeping active tables performant.

## Architecture

- **Main Schema (public)**: Active, current data
- **Archive Schema (archive)**: Historical, archived data (read-only)

## What Gets Archived

The following data types can be archived:

1. **Orders**: Completed, cancelled, or rejected orders older than X years
2. **Complaints**: Resolved complaints older than X years
3. **Incidents**: Resolved incidents older than X years
4. **Messages**: Messages older than X years (archived by link)
5. **Links**: Removed or blocked links older than X years

## How It Works

### Database Functions

The migration creates PostgreSQL functions for archiving:

- `archive_order(order_id)` - Archives an order and its items
- `archive_complaint(complaint_id)` - Archives a complaint
- `archive_incident(incident_id)` - Archives an incident
- `archive_messages_by_link(link_id)` - Archives all messages for a link
- `archive_link(link_id)` - Archives a link and its messages

### Archival Script

Use the provided Python script to archive old data:

```bash
# Dry run (see what would be archived)
python scripts/archive_old_data.py --years=3 --dry-run

# Archive all data older than 3 years
python scripts/archive_old_data.py --years=3

# Archive only orders older than 5 years
python scripts/archive_old_data.py --years=5 --type=orders

# Archive only complaints
python scripts/archive_old_data.py --years=3 --type=complaints
```

### Automated Archival

Set up a cron job or scheduled task to run the archival script periodically:

```bash
# Example cron job (runs monthly on 1st at 2 AM)
0 2 1 * * cd /path/to/backend && python scripts/archive_old_data.py --years=3
```

## Accessing Archived Data

### Direct Database Query

Archived data can be queried directly from the `archive` schema:

```sql
-- View archived orders
SELECT * FROM archive.orders WHERE supplier_id = 1;

-- View archived complaints
SELECT * FROM archive.complaints WHERE status = 'RESOLVED';
```

### API Access (Future)

You can add API endpoints to access archived data if needed. Example:

```python
@router.get("/archive/orders")
async def get_archived_orders(...):
    # Query archive.orders table
    pass
```

## Important Notes

1. **No Foreign Keys**: Archive tables don't have foreign key constraints to avoid dependency issues
2. **Read-Only**: Archived data should be treated as read-only
3. **Backup**: Archive schema should be included in database backups
4. **Retention Period**: Default is 3 years, but can be configured per organization
5. **Cascade**: When archiving orders, order_items are automatically archived
6. **Cascade**: When archiving links, messages are automatically archived

## Migration

To set up the archive schema:

```bash
cd backend
alembic upgrade head
```

This will:
- Create the `archive` schema
- Create archive tables for orders, order_items, complaints, incidents, messages, and links
- Create PostgreSQL functions for archiving

## Rollback

If you need to rollback the archive schema:

```bash
alembic downgrade -1
```

**Warning**: This will drop the archive schema and all archived data. Make sure you have backups!

## Best Practices

1. **Test First**: Always run with `--dry-run` first
2. **Backup**: Backup database before archiving
3. **Monitor**: Check archive schema size periodically
4. **Retention Policy**: Document your retention policy (e.g., 3 years for compliance)
5. **Access Control**: Limit access to archive schema (read-only for most users)

## Troubleshooting

### Error: "schema archive does not exist"
Run the migration: `alembic upgrade head`

### Error: "function archive_order does not exist"
The migration may not have run completely. Check migration status: `alembic current`

### Archive script fails
- Check database connection
- Verify migration has been applied
- Check PostgreSQL logs for detailed errors

