#!/usr/bin/env python3
"""
Migration verification script for commute-cards production deployment.

Run BEFORE deployment to check current state:
    fly ssh console -C "python scripts/verify-migration.py --check"

Run AFTER deployment to verify migration:
    fly ssh console -C "python scripts/verify-migration.py --verify"

Or run locally with DATABASE_URL set:
    DATABASE_URL=... python scripts/verify-migration.py --check
"""

import os
import sys
import argparse

try:
    import psycopg
except ImportError:
    print("Error: psycopg not installed. Run: pip install psycopg[binary]")
    sys.exit(1)


def get_db():
    """Get database connection from DATABASE_URL."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL not set")
        sys.exit(1)
    return psycopg.connect(db_url)


def check_pre_deployment():
    """Check current state before deployment."""
    print("=" * 60)
    print("PRE-DEPLOYMENT CHECK")
    print("=" * 60)

    with get_db() as conn:
        with conn.cursor() as cur:
            # Count cards
            cur.execute("SELECT COUNT(*) FROM cards")
            card_count = cur.fetchone()[0]
            print(f"\nCards in database: {card_count}")

            # Check if new columns exist
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'cards' AND column_name IN ('visibility', 'device_token', 'card_type')
            """)
            existing_columns = [row[0] for row in cur.fetchall()]
            print(f"New columns already exist: {existing_columns or 'None'}")

            # Count responses
            cur.execute("SELECT COUNT(*) FROM responses")
            response_count = cur.fetchone()[0]
            print(f"Responses in database: {response_count}")

            # Sample card IDs
            cur.execute("SELECT id, semantic_description FROM cards ORDER BY id LIMIT 5")
            print("\nSample cards:")
            for row in cur.fetchall():
                desc = row[1][:50] + "..." if len(row[1]) > 50 else row[1]
                print(f"  ID {row[0]}: {desc}")

    print("\n" + "=" * 60)
    print("Pre-deployment check complete. Safe to deploy if cards look correct.")
    print("=" * 60)


def verify_post_deployment():
    """Verify migration after deployment."""
    print("=" * 60)
    print("POST-DEPLOYMENT VERIFICATION")
    print("=" * 60)

    errors = []

    with get_db() as conn:
        with conn.cursor() as cur:
            # Check new columns exist
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'cards' AND column_name IN ('visibility', 'device_token', 'card_type')
            """)
            columns = [row[0] for row in cur.fetchall()]

            if 'visibility' not in columns:
                errors.append("Missing column: visibility")
            if 'device_token' not in columns:
                errors.append("Missing column: device_token")
            if 'card_type' not in columns:
                errors.append("Missing column: card_type")

            print(f"\nNew columns present: {columns}")

            # Check all cards are public
            cur.execute("SELECT COUNT(*) FROM cards WHERE visibility = 'public' OR visibility IS NULL")
            public_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM cards")
            total_count = cur.fetchone()[0]

            print(f"Total cards: {total_count}")
            print(f"Public cards: {public_count}")

            if public_count != total_count:
                cur.execute("SELECT COUNT(*) FROM cards WHERE visibility != 'public' AND visibility IS NOT NULL")
                non_public = cur.fetchone()[0]
                print(f"WARNING: {non_public} cards are not public")

            # Check card_type defaults
            cur.execute("SELECT card_type, COUNT(*) FROM cards GROUP BY card_type")
            print("\nCards by type:")
            for row in cur.fetchall():
                print(f"  {row[0] or 'NULL'}: {row[1]}")

            # Check responses have device_token column
            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'responses' AND column_name = 'device_token'
            """)
            if not cur.fetchone():
                errors.append("Missing column in responses: device_token")
            else:
                print("\nResponses table has device_token column: ✓")

            # Check feedback table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'feedback'
                )
            """)
            if cur.fetchone()[0]:
                print("Feedback table exists: ✓")
            else:
                errors.append("Missing table: feedback")

    print("\n" + "=" * 60)
    if errors:
        print("VERIFICATION FAILED!")
        for error in errors:
            print(f"  ✗ {error}")
        sys.exit(1)
    else:
        print("VERIFICATION PASSED! All migrations applied successfully.")
    print("=" * 60)


def fix_visibility():
    """Fix any NULL visibility values to 'public'."""
    print("Fixing NULL visibility values...")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE cards SET visibility = 'public' WHERE visibility IS NULL")
            updated = cur.rowcount
            conn.commit()
            print(f"Updated {updated} cards to visibility='public'")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify commute-cards migration')
    parser.add_argument('--check', action='store_true', help='Pre-deployment check')
    parser.add_argument('--verify', action='store_true', help='Post-deployment verification')
    parser.add_argument('--fix', action='store_true', help='Fix NULL visibility values')

    args = parser.parse_args()

    if args.check:
        check_pre_deployment()
    elif args.verify:
        verify_post_deployment()
    elif args.fix:
        fix_visibility()
    else:
        parser.print_help()