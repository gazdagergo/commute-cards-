"""
Migration: 001_task_pages
Description: Add task pages tables for standalone learning content

Creates:
    - task_pages: Standalone LLM-generated learning pages
    - task_page_statuses: Per-device progress tracking
    - task_page_responses: User submissions for task pages
    - Adds task_page_id column to cards table

Usage:
    python migrations/001_task_pages.py up      # Apply
    python migrations/001_task_pages.py down    # Rollback
    python migrations/001_task_pages.py status  # Check status
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migrations.runner import run_migration


def up(conn):
    """Apply migration - create task pages tables."""
    with conn.cursor() as cur:
        # ==========================================================
        # TASK PAGES TABLE
        # Standalone LLM-generated learning content
        # ==========================================================
        print("  Creating task_pages table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS task_pages (
                id VARCHAR(64) PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- Content
                title VARCHAR(255) NOT NULL,
                description TEXT,
                page_html TEXT NOT NULL,

                -- Organization
                course_id INTEGER REFERENCES courses(id),
                topics TEXT[],

                -- Metadata
                estimated_duration_minutes INTEGER,
                difficulty VARCHAR(20),
                generation_batch VARCHAR(64)
            )
        """)

        # ==========================================================
        # TASK PAGE STATUSES TABLE
        # Per-device progress tracking for task pages
        # ==========================================================
        print("  Creating task_page_statuses table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS task_page_statuses (
                id SERIAL PRIMARY KEY,
                task_page_id VARCHAR(64) REFERENCES task_pages(id) ON DELETE CASCADE,
                device_token VARCHAR(64) NOT NULL,

                status VARCHAR(20) DEFAULT 'not_started',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                -- Local notes backup (optional)
                notes TEXT,

                UNIQUE(task_page_id, device_token)
            )
        """)

        # ==========================================================
        # TASK PAGE RESPONSES TABLE
        # User submissions for task pages
        # ==========================================================
        print("  Creating task_page_responses table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS task_page_responses (
                id SERIAL PRIMARY KEY,
                task_page_id VARCHAR(64) REFERENCES task_pages(id) ON DELETE CASCADE,
                device_token VARCHAR(64) NOT NULL,

                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_content JSONB NOT NULL,

                -- Evaluation (filled by LLM later)
                evaluation JSONB,
                evaluated_at TIMESTAMP
            )
        """)

        # ==========================================================
        # ADD task_page_id TO CARDS TABLE
        # Cards can now reference task pages
        # ==========================================================
        print("  Adding task_page_id column to cards...")
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'cards' AND column_name = 'task_page_id'
                ) THEN
                    ALTER TABLE cards ADD COLUMN task_page_id VARCHAR(64) REFERENCES task_pages(id);
                END IF;
            END $$;
        """)

        # ==========================================================
        # INDEXES
        # ==========================================================
        print("  Creating indexes...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_pages_course
            ON task_pages(course_id)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_page_statuses_device
            ON task_page_statuses(device_token)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_page_statuses_lookup
            ON task_page_statuses(task_page_id, device_token)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_task_page_responses_lookup
            ON task_page_responses(task_page_id, device_token)
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_cards_task_page
            ON cards(task_page_id)
        """)

    conn.commit()
    print("  Done.")


def down(conn):
    """Rollback migration - drop task pages tables."""
    with conn.cursor() as cur:
        # Drop in reverse order due to foreign key constraints

        # ==========================================================
        # REMOVE task_page_id FROM CARDS TABLE
        # ==========================================================
        print("  Removing task_page_id column from cards...")
        cur.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'cards' AND column_name = 'task_page_id'
                ) THEN
                    ALTER TABLE cards DROP COLUMN task_page_id;
                END IF;
            END $$;
        """)

        # ==========================================================
        # DROP INDEXES (will be dropped with tables, but explicit for clarity)
        # ==========================================================
        print("  Dropping indexes...")
        cur.execute("DROP INDEX IF EXISTS idx_task_page_responses_lookup")
        cur.execute("DROP INDEX IF EXISTS idx_task_page_statuses_lookup")
        cur.execute("DROP INDEX IF EXISTS idx_task_page_statuses_device")
        cur.execute("DROP INDEX IF EXISTS idx_task_pages_course")
        cur.execute("DROP INDEX IF EXISTS idx_cards_task_page")

        # ==========================================================
        # DROP TABLES
        # ==========================================================
        print("  Dropping task_page_responses table...")
        cur.execute("DROP TABLE IF EXISTS task_page_responses")

        print("  Dropping task_page_statuses table...")
        cur.execute("DROP TABLE IF EXISTS task_page_statuses")

        print("  Dropping task_pages table...")
        cur.execute("DROP TABLE IF EXISTS task_pages")

    conn.commit()
    print("  Done.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    run_migration(__file__, action, up, down)