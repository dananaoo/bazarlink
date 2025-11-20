"""
Script to archive old data based on retention policy.

This script archives records older than specified years:
- Orders: 3 years (configurable)
- Complaints: 3 years (configurable)
- Incidents: 3 years (configurable)
- Messages: 3 years (configurable)
- Links: 3 years (configurable)

Usage:
    python scripts/archive_old_data.py [--years=3] [--dry-run]
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path BEFORE importing app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.db.session import SessionLocal


def archive_old_orders(db, years: int, dry_run: bool = False):
    """Archive orders older than specified years"""
    cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
    
    # Find orders to archive
    result = db.execute(text("""
        SELECT id FROM orders 
        WHERE created_at < :cutoff_date
        AND status IN ('COMPLETED', 'CANCELLED', 'REJECTED')
        ORDER BY id
    """), {"cutoff_date": cutoff_date})
    
    order_ids = [row[0] for row in result]
    
    if not order_ids:
        print(f"No orders to archive (older than {years} years)")
        return 0
    
    print(f"Found {len(order_ids)} orders to archive")
    
    if dry_run:
        print(f"DRY RUN: Would archive orders: {order_ids[:10]}..." if len(order_ids) > 10 else f"DRY RUN: Would archive orders: {order_ids}")
        return len(order_ids)
    
    archived_count = 0
    for order_id in order_ids:
        try:
            db.execute(text("SELECT archive_order(:order_id)"), {"order_id": order_id})
            archived_count += 1
            if archived_count % 10 == 0:
                print(f"Archived {archived_count}/{len(order_ids)} orders...")
        except Exception as e:
            print(f"Error archiving order {order_id}: {e}")
    
    db.commit()
    print(f"Archived {archived_count} orders")
    return archived_count


def archive_old_complaints(db, years: int, dry_run: bool = False):
    """Archive resolved complaints older than specified years"""
    cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
    
    result = db.execute(text("""
        SELECT id FROM complaints 
        WHERE status = 'RESOLVED'
        AND resolved_at < :cutoff_date
        ORDER BY id
    """), {"cutoff_date": cutoff_date})
    
    complaint_ids = [row[0] for row in result]
    
    if not complaint_ids:
        print(f"No complaints to archive (resolved more than {years} years ago)")
        return 0
    
    print(f"Found {len(complaint_ids)} complaints to archive")
    
    if dry_run:
        print(f"DRY RUN: Would archive complaints: {complaint_ids[:10]}..." if len(complaint_ids) > 10 else f"DRY RUN: Would archive complaints: {complaint_ids}")
        return len(complaint_ids)
    
    archived_count = 0
    for complaint_id in complaint_ids:
        try:
            db.execute(text("SELECT archive_complaint(:complaint_id)"), {"complaint_id": complaint_id})
            archived_count += 1
        except Exception as e:
            print(f"Error archiving complaint {complaint_id}: {e}")
    
    db.commit()
    print(f"Archived {archived_count} complaints")
    return archived_count


def archive_old_incidents(db, years: int, dry_run: bool = False):
    """Archive resolved incidents older than specified years"""
    cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
    
    result = db.execute(text("""
        SELECT id FROM incidents 
        WHERE status = 'RESOLVED'
        AND resolved_at < :cutoff_date
        ORDER BY id
    """), {"cutoff_date": cutoff_date})
    
    incident_ids = [row[0] for row in result]
    
    if not incident_ids:
        print(f"No incidents to archive (resolved more than {years} years ago)")
        return 0
    
    print(f"Found {len(incident_ids)} incidents to archive")
    
    if dry_run:
        print(f"DRY RUN: Would archive incidents: {incident_ids[:10]}..." if len(incident_ids) > 10 else f"DRY RUN: Would archive incidents: {incident_ids}")
        return len(incident_ids)
    
    archived_count = 0
    for incident_id in incident_ids:
        try:
            db.execute(text("SELECT archive_incident(:incident_id)"), {"incident_id": incident_id})
            archived_count += 1
        except Exception as e:
            print(f"Error archiving incident {incident_id}: {e}")
    
    db.commit()
    print(f"Archived {archived_count} incidents")
    return archived_count


def archive_old_messages(db, years: int, dry_run: bool = False):
    """Archive messages older than specified years"""
    cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
    
    result = db.execute(text("""
        SELECT DISTINCT link_id FROM messages 
        WHERE created_at < :cutoff_date
        ORDER BY link_id
    """), {"cutoff_date": cutoff_date})
    
    link_ids = [row[0] for row in result]
    
    if not link_ids:
        print(f"No messages to archive (older than {years} years)")
        return 0
    
    print(f"Found messages from {len(link_ids)} links to archive")
    
    if dry_run:
        print(f"DRY RUN: Would archive messages from links: {link_ids[:10]}..." if len(link_ids) > 10 else f"DRY RUN: Would archive messages from links: {link_ids}")
        return len(link_ids)
    
    archived_count = 0
    for link_id in link_ids:
        try:
            db.execute(text("SELECT archive_messages_by_link(:link_id)"), {"link_id": link_id})
            archived_count += 1
        except Exception as e:
            print(f"Error archiving messages for link {link_id}: {e}")
    
    db.commit()
    print(f"Archived messages from {archived_count} links")
    return archived_count


def archive_old_links(db, years: int, dry_run: bool = False):
    """Archive links (REMOVED or BLOCKED) older than specified years"""
    cutoff_date = datetime.utcnow() - timedelta(days=years * 365)
    
    result = db.execute(text("""
        SELECT id FROM links 
        WHERE status IN ('REMOVED', 'BLOCKED')
        AND updated_at < :cutoff_date
        ORDER BY id
    """), {"cutoff_date": cutoff_date})
    
    link_ids = [row[0] for row in result]
    
    if not link_ids:
        print(f"No links to archive (REMOVED/BLOCKED more than {years} years ago)")
        return 0
    
    print(f"Found {len(link_ids)} links to archive")
    
    if dry_run:
        print(f"DRY RUN: Would archive links: {link_ids[:10]}..." if len(link_ids) > 10 else f"DRY RUN: Would archive links: {link_ids}")
        return len(link_ids)
    
    archived_count = 0
    for link_id in link_ids:
        try:
            db.execute(text("SELECT archive_link(:link_id)"), {"link_id": link_id})
            archived_count += 1
        except Exception as e:
            print(f"Error archiving link {link_id}: {e}")
    
    db.commit()
    print(f"Archived {archived_count} links")
    return archived_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Archive old data based on retention policy")
    parser.add_argument("--years", type=int, default=3, help="Number of years for retention (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be archived without actually archiving")
    parser.add_argument("--type", choices=["orders", "complaints", "incidents", "messages", "links", "all"], 
                       default="all", help="Type of data to archive (default: all)")
    
    args = parser.parse_args()
    
    db = SessionLocal()
    
    try:
        print(f"Starting archive process (retention: {args.years} years, dry-run: {args.dry_run})")
        print("=" * 60)
        
        total_archived = 0
        
        if args.type in ["orders", "all"]:
            print("\n--- Archiving Orders ---")
            total_archived += archive_old_orders(db, args.years, args.dry_run)
        
        if args.type in ["complaints", "all"]:
            print("\n--- Archiving Complaints ---")
            total_archived += archive_old_complaints(db, args.years, args.dry_run)
        
        if args.type in ["incidents", "all"]:
            print("\n--- Archiving Incidents ---")
            total_archived += archive_old_incidents(db, args.years, args.dry_run)
        
        if args.type in ["messages", "all"]:
            print("\n--- Archiving Messages ---")
            total_archived += archive_old_messages(db, args.years, args.dry_run)
        
        if args.type in ["links", "all"]:
            print("\n--- Archiving Links ---")
            total_archived += archive_old_links(db, args.years, args.dry_run)
        
        print("\n" + "=" * 60)
        if args.dry_run:
            print(f"DRY RUN: Would archive {total_archived} total records")
        else:
            print(f"Archived {total_archived} total records")
        
    except Exception as e:
        print(f"Error during archiving: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

