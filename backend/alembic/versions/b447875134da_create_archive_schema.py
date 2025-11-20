"""create_archive_schema

Revision ID: b447875134da
Revises: 1b4f8ca0e372
Create Date: 2025-11-21 01:17:31.993212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b447875134da'
down_revision: Union[str, None] = '1b4f8ca0e372'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Create archive schema for data retention.
    
    Creates a separate 'archive' schema in PostgreSQL to store archived records
    for compliance and data retention purposes. Tables in archive schema have
    the same structure as main tables but without foreign key constraints
    (to avoid dependency issues with archived data).
    """
    # Step 1: Create archive schema
    op.execute("CREATE SCHEMA IF NOT EXISTS archive")
    
    # Step 2: Create archive.orders table
    op.execute("""
        CREATE TABLE archive.orders (
            id INTEGER PRIMARY KEY,
            supplier_id INTEGER NOT NULL,
            consumer_id INTEGER NOT NULL,
            order_number VARCHAR NOT NULL,
            status VARCHAR NOT NULL,
            delivery_method VARCHAR,
            delivery_address TEXT,
            delivery_date TIMESTAMP WITH TIME ZONE,
            subtotal NUMERIC(10, 2) NOT NULL,
            total NUMERIC(10, 2) NOT NULL,
            currency VARCHAR,
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            accepted_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_orders_supplier_id ON archive.orders(supplier_id)")
    op.execute("CREATE INDEX idx_archive_orders_consumer_id ON archive.orders(consumer_id)")
    op.execute("CREATE INDEX idx_archive_orders_order_number ON archive.orders(order_number)")
    op.execute("CREATE INDEX idx_archive_orders_status ON archive.orders(status)")
    op.execute("CREATE INDEX idx_archive_orders_archived_at ON archive.orders(archived_at)")
    
    # Step 3: Create archive.order_items table
    op.execute("""
        CREATE TABLE archive.order_items (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity NUMERIC(10, 2) NOT NULL,
            unit_price NUMERIC(10, 2) NOT NULL,
            total_price NUMERIC(10, 2) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_order_items_order_id ON archive.order_items(order_id)")
    
    # Step 4: Create archive.complaints table
    op.execute("""
        CREATE TABLE archive.complaints (
            id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            consumer_id INTEGER NOT NULL,
            supplier_id INTEGER NOT NULL,
            link_id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR NOT NULL,
            level VARCHAR NOT NULL,
            escalated_to_user_id INTEGER,
            escalated_by_user_id INTEGER,
            resolution TEXT,
            resolved_by_user_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            resolved_at TIMESTAMP WITH TIME ZONE,
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_complaints_order_id ON archive.complaints(order_id)")
    op.execute("CREATE INDEX idx_archive_complaints_consumer_id ON archive.complaints(consumer_id)")
    op.execute("CREATE INDEX idx_archive_complaints_supplier_id ON archive.complaints(supplier_id)")
    op.execute("CREATE INDEX idx_archive_complaints_link_id ON archive.complaints(link_id)")
    op.execute("CREATE INDEX idx_archive_complaints_status ON archive.complaints(status)")
    op.execute("CREATE INDEX idx_archive_complaints_archived_at ON archive.complaints(archived_at)")
    
    # Step 5: Create archive.incidents table
    op.execute("""
        CREATE TABLE archive.incidents (
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            consumer_id INTEGER,
            supplier_id INTEGER,
            title VARCHAR NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR NOT NULL,
            assigned_to_user_id INTEGER,
            created_by_user_id INTEGER NOT NULL,
            resolution TEXT,
            resolved_by_user_id INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            resolved_at TIMESTAMP WITH TIME ZONE,
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_incidents_supplier_id ON archive.incidents(supplier_id)")
    op.execute("CREATE INDEX idx_archive_incidents_consumer_id ON archive.incidents(consumer_id)")
    op.execute("CREATE INDEX idx_archive_incidents_order_id ON archive.incidents(order_id)")
    op.execute("CREATE INDEX idx_archive_incidents_status ON archive.incidents(status)")
    op.execute("CREATE INDEX idx_archive_incidents_archived_at ON archive.incidents(archived_at)")
    
    # Step 6: Create archive.messages table
    op.execute("""
        CREATE TABLE archive.messages (
            id INTEGER PRIMARY KEY,
            link_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER,
            sales_rep_id INTEGER,
            content TEXT NOT NULL,
            message_type VARCHAR,
            attachment_url VARCHAR,
            attachment_type VARCHAR,
            product_id INTEGER,
            order_id INTEGER,
            is_canned_reply BOOLEAN,
            canned_reply_id INTEGER,
            is_read BOOLEAN,
            read_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_messages_link_id ON archive.messages(link_id)")
    op.execute("CREATE INDEX idx_archive_messages_sender_id ON archive.messages(sender_id)")
    op.execute("CREATE INDEX idx_archive_messages_receiver_id ON archive.messages(receiver_id)")
    op.execute("CREATE INDEX idx_archive_messages_sales_rep_id ON archive.messages(sales_rep_id)")
    op.execute("CREATE INDEX idx_archive_messages_archived_at ON archive.messages(archived_at)")
    
    # Step 7: Create archive.links table
    op.execute("""
        CREATE TABLE archive.links (
            id INTEGER PRIMARY KEY,
            supplier_id INTEGER NOT NULL,
            consumer_id INTEGER NOT NULL,
            status VARCHAR NOT NULL,
            requested_by_consumer BOOLEAN,
            request_message VARCHAR,
            assigned_sales_rep_id INTEGER,
            requested_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            responded_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
            updated_at TIMESTAMP WITH TIME ZONE,
            archived_at TIMESTAMP WITH TIME ZONE DEFAULT now()
        )
    """)
    op.execute("CREATE INDEX idx_archive_links_supplier_id ON archive.links(supplier_id)")
    op.execute("CREATE INDEX idx_archive_links_consumer_id ON archive.links(consumer_id)")
    op.execute("CREATE INDEX idx_archive_links_status ON archive.links(status)")
    op.execute("CREATE INDEX idx_archive_links_archived_at ON archive.links(archived_at)")
    
    # Step 8: Create function to archive orders (and related data)
    op.execute("""
        CREATE OR REPLACE FUNCTION archive_order(order_id_to_archive INTEGER)
        RETURNS VOID AS $$
        BEGIN
            -- Archive order items first
            INSERT INTO archive.order_items 
            SELECT *, now() as archived_at 
            FROM order_items 
            WHERE order_id = order_id_to_archive;
            
            -- Archive order
            INSERT INTO archive.orders 
            SELECT *, now() as archived_at 
            FROM orders 
            WHERE id = order_id_to_archive;
            
            -- Delete from main tables (cascade will handle order_items)
            DELETE FROM orders WHERE id = order_id_to_archive;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Step 9: Create function to archive complaints
    op.execute("""
        CREATE OR REPLACE FUNCTION archive_complaint(complaint_id_to_archive INTEGER)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO archive.complaints 
            SELECT *, now() as archived_at 
            FROM complaints 
            WHERE id = complaint_id_to_archive;
            
            DELETE FROM complaints WHERE id = complaint_id_to_archive;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Step 10: Create function to archive incidents
    op.execute("""
        CREATE OR REPLACE FUNCTION archive_incident(incident_id_to_archive INTEGER)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO archive.incidents 
            SELECT *, now() as archived_at 
            FROM incidents 
            WHERE id = incident_id_to_archive;
            
            DELETE FROM incidents WHERE id = incident_id_to_archive;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Step 11: Create function to archive messages by link_id
    op.execute("""
        CREATE OR REPLACE FUNCTION archive_messages_by_link(link_id_to_archive INTEGER)
        RETURNS VOID AS $$
        BEGIN
            INSERT INTO archive.messages 
            SELECT *, now() as archived_at 
            FROM messages 
            WHERE link_id = link_id_to_archive;
            
            DELETE FROM messages WHERE link_id = link_id_to_archive;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Step 12: Create function to archive links
    op.execute("""
        CREATE OR REPLACE FUNCTION archive_link(link_id_to_archive INTEGER)
        RETURNS VOID AS $$
        BEGIN
            -- Archive messages first
            PERFORM archive_messages_by_link(link_id_to_archive);
            
            -- Archive link
            INSERT INTO archive.links 
            SELECT *, now() as archived_at 
            FROM links 
            WHERE id = link_id_to_archive;
            
            DELETE FROM links WHERE id = link_id_to_archive;
        END;
        $$ LANGUAGE plpgsql;
    """)


def downgrade() -> None:
    """Downgrade schema - Remove archive schema and functions."""
    # Drop functions first
    op.execute("DROP FUNCTION IF EXISTS archive_link(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS archive_messages_by_link(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS archive_incident(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS archive_complaint(INTEGER)")
    op.execute("DROP FUNCTION IF EXISTS archive_order(INTEGER)")
    
    # Drop tables
    op.execute("DROP TABLE IF EXISTS archive.links CASCADE")
    op.execute("DROP TABLE IF EXISTS archive.messages CASCADE")
    op.execute("DROP TABLE IF EXISTS archive.incidents CASCADE")
    op.execute("DROP TABLE IF EXISTS archive.complaints CASCADE")
    op.execute("DROP TABLE IF EXISTS archive.order_items CASCADE")
    op.execute("DROP TABLE IF EXISTS archive.orders CASCADE")
    
    # Drop schema
    op.execute("DROP SCHEMA IF EXISTS archive CASCADE")
