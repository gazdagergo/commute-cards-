"""
Migration runner utility.

Usage:
    python migrations/001_task_pages.py up      # Apply migration
    python migrations/001_task_pages.py down    # Rollback migration
    python migrations/001_task_pages.py status  # Check if applied

Environment:
    DATABASE_URL: PostgreSQL connection string
"""

import os
import sys
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/sociology_learning_pwa")


def get_connection():
    """Get database connection."""
    return psycopg.connect(DATABASE_URL)


def ensure_migrations_table(conn):
    """Create migrations tracking table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    conn.commit()


def is_applied(conn, migration_name):
    """Check if a migration has been applied."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM schema_migrations WHERE migration_name = %s",
            (migration_name,)
        )
        return cur.fetchone() is not None


def mark_applied(conn, migration_name):
    """Mark a migration as applied."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
            (migration_name,)
        )
    conn.commit()


def mark_unapplied(conn, migration_name):
    """Remove migration from applied list."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM schema_migrations WHERE migration_name = %s",
            (migration_name,)
        )
    conn.commit()


def run_migration(migration_file, action, up_fn, down_fn):
    """
    Run a migration.

    Args:
        migration_file: __file__ from the migration script
        action: 'up', 'down', or 'status'
        up_fn: Function to apply migration (receives conn)
        down_fn: Function to rollback migration (receives conn)
    """
    # Extract migration name from filename
    migration_name = os.path.basename(migration_file).replace('.py', '')

    print(f"Migration: {migration_name}")
    print(f"Action: {action}")
    print(f"Database: {DATABASE_URL[:50]}...")
    print("-" * 50)

    conn = get_connection()
    ensure_migrations_table(conn)

    applied = is_applied(conn, migration_name)

    if action == "status":
        if applied:
            print(f"✓ Migration {migration_name} is APPLIED")
        else:
            print(f"✗ Migration {migration_name} is NOT applied")
        conn.close()
        return

    if action == "up":
        if applied:
            print(f"Migration {migration_name} is already applied. Skipping.")
            conn.close()
            return

        print(f"Applying migration {migration_name}...")
        try:
            up_fn(conn)
            mark_applied(conn, migration_name)
            print(f"✓ Migration {migration_name} applied successfully")
        except Exception as e:
            print(f"✗ Migration failed: {e}")
            conn.rollback()
            raise

    elif action == "down":
        if not applied:
            print(f"Migration {migration_name} is not applied. Nothing to rollback.")
            conn.close()
            return

        print(f"Rolling back migration {migration_name}...")
        try:
            down_fn(conn)
            mark_unapplied(conn, migration_name)
            print(f"✓ Migration {migration_name} rolled back successfully")
        except Exception as e:
            print(f"✗ Rollback failed: {e}")
            conn.rollback()
            raise

    else:
        print(f"Unknown action: {action}")
        print("Usage: python migration.py [up|down|status]")
        sys.exit(1)

    conn.close()
