import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from markupsafe import Markup
import psycopg

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/sociology_learning_pwa")


def get_db():
    """Get a database connection."""
    return psycopg.connect(DATABASE_URL)


def init_db():
    """Create tables if they don't exist."""
    import sys
    print("Starting init_db...", file=sys.stderr)
    try:
        conn = get_db()
        print("Connected to database", file=sys.stderr)
    except Exception as e:
        print(f"Failed to connect: {e}", file=sys.stderr)
        raise

    with conn:
        with conn.cursor() as cur:
            print("Creating cards table...", file=sys.stderr)
            # Cards table - open educational resources
            # Status/progress is NOT stored here - it lives in device IndexedDB
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    semantic_description TEXT NOT NULL,
                    course_task_ref VARCHAR(255),
                    card_html TEXT NOT NULL,
                    response_schema JSONB NOT NULL,
                    visibility VARCHAR(20) DEFAULT 'public',
                    device_token VARCHAR(64),
                    card_type VARCHAR(20) DEFAULT 'learning',
                    parent_response_id INTEGER,
                    generation_batch VARCHAR(64)
                )
            """)

            print("Cards table done", file=sys.stderr)

            # Responses table - anonymous submissions linked by device token
            print("Creating responses table...", file=sys.stderr)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
                    device_token VARCHAR(64) NOT NULL,
                    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_content JSONB NOT NULL,
                    evaluated BOOLEAN DEFAULT FALSE,
                    evaluated_at TIMESTAMP,
                    evaluation_card_id INTEGER
                )
            """)

            # Feedback table - optional card ratings
            cur.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    response_id INTEGER REFERENCES responses(id) ON DELETE CASCADE,
                    device_token VARCHAR(64) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                    comment TEXT
                )
            """)

            print("Tables created, running migrations...", file=sys.stderr)

            # ==========================================================
            # MIGRATIONS - Run BEFORE indexes to add missing columns
            # These handle upgrading from the old schema
            # ==========================================================

            # Migration: Add visibility column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'visibility'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN visibility VARCHAR(20) DEFAULT 'public';
                    END IF;
                END $$;
            """)

            # Migration: Add device_token column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'device_token'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN device_token VARCHAR(64);
                    END IF;
                END $$;
            """)

            # Migration: Add card_type column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'card_type'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN card_type VARCHAR(20) DEFAULT 'learning';
                    END IF;
                END $$;
            """)

            # Migration: Add parent_response_id column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'parent_response_id'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN parent_response_id INTEGER;
                    END IF;
                END $$;
            """)

            # Migration: Add generation_batch column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'generation_batch'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN generation_batch VARCHAR(64);
                    END IF;
                END $$;
            """)

            # Migration: Add device_token column to responses
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'responses' AND column_name = 'device_token'
                    ) THEN
                        ALTER TABLE responses ADD COLUMN device_token VARCHAR(64);
                        -- Set a placeholder for existing responses
                        UPDATE responses SET device_token = 'legacy-migration' WHERE device_token IS NULL;
                    END IF;
                END $$;
            """)

            # Migration: Add evaluated column to responses
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'responses' AND column_name = 'evaluated'
                    ) THEN
                        ALTER TABLE responses ADD COLUMN evaluated BOOLEAN DEFAULT FALSE;
                    END IF;
                END $$;
            """)

            # Migration: Add evaluated_at column to responses
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'responses' AND column_name = 'evaluated_at'
                    ) THEN
                        ALTER TABLE responses ADD COLUMN evaluated_at TIMESTAMP;
                    END IF;
                END $$;
            """)

            # Migration: Add evaluation_card_id column to responses
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'responses' AND column_name = 'evaluation_card_id'
                    ) THEN
                        ALTER TABLE responses ADD COLUMN evaluation_card_id INTEGER;
                    END IF;
                END $$;
            """)

            # ==========================================================
            # COURSES - Course filtering system
            # ==========================================================
            print("Creating courses table...", file=sys.stderr)

            # Courses table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS courses (
                    id SERIAL PRIMARY KEY,
                    slug VARCHAR(64) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT
                )
            """)

            # Migration: Add course_id column to cards
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'course_id'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN course_id INTEGER REFERENCES courses(id);
                    END IF;
                END $$;
            """)

            # Seed default courses if they don't exist
            cur.execute("""
                INSERT INTO courses (slug, name, description)
                VALUES ('sociology', 'Soziologie', 'Einführung in die Soziologie - Übungen A, B, C, etc.')
                ON CONFLICT (slug) DO NOTHING
            """)
            cur.execute("""
                INSERT INTO courses (slug, name, description)
                VALUES ('ml-basics', 'ML Basics', 'Machine Learning fundamentals - Hello World Model')
                ON CONFLICT (slug) DO NOTHING
            """)

            # Migrate existing cards to courses based on course_task_ref
            # Cards with ml-* refs go to ml-basics, others go to sociology
            cur.execute("""
                UPDATE cards
                SET course_id = (SELECT id FROM courses WHERE slug = 'ml-basics')
                WHERE course_id IS NULL
                  AND (course_task_ref LIKE 'ml-%' OR semantic_description LIKE 'ML %')
            """)
            cur.execute("""
                UPDATE cards
                SET course_id = (SELECT id FROM courses WHERE slug = 'sociology')
                WHERE course_id IS NULL
            """)

            print("Courses setup done", file=sys.stderr)

            print("Migrations done, creating indexes...", file=sys.stderr)

            # ==========================================================
            # INDEXES - Created AFTER migrations to ensure columns exist
            # ==========================================================
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cards_visibility ON cards(visibility)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cards_device_token ON cards(device_token)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_responses_device_token ON responses(device_token)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_responses_not_evaluated
                ON responses(evaluated) WHERE evaluated = FALSE
            """)

            print("Indexes created", file=sys.stderr)

            # Seed a sample card if the database is empty
            cur.execute("SELECT COUNT(*) FROM cards")
            if cur.fetchone()[0] == 0:
                sample_card_html = '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Lernziel: Grundbegriff der Soziologie verstehen</p>
        <h2 class="text-lg font-semibold mb-4">Was versteht man unter dem Begriff "Sozialisation"?</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="5"
                  placeholder="Schreibe deine Antwort..."></textarea>

        <button @click="submitResponse({ answer })"
                :disabled="submitting || answer.trim().length < 10"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>'''
                sample_schema = json.dumps({
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string"}
                    },
                    "required": ["answer"]
                })
                cur.execute(
                    """INSERT INTO cards (semantic_description, card_html, response_schema, visibility, card_type)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (
                        "Define the concept of socialization (Sozialisation) - fundamental sociology term",
                        sample_card_html,
                        sample_schema,
                        "public",
                        "learning"
                    )
                )
        conn.commit()


@app.route("/")
def index():
    """Main app view - renders the card interface."""
    return render_template("index.html")


# ==========================================================
# PUBLIC API - No authentication required
# ==========================================================

@app.route("/api/courses")
def api_courses():
    """Get available courses."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, slug, name, description
                FROM courses
                ORDER BY name ASC
            """)
            rows = cur.fetchall()

            courses = []
            for row in rows:
                courses.append({
                    "id": row[0],
                    "slug": row[1],
                    "name": row[2],
                    "description": row[3]
                })

            return jsonify({
                "courses": courses
            })


@app.route("/api/cards")
def api_cards():
    """Get cards - public cards and optionally device-specific private cards.

    Query params:
    - device_token: Include private cards for this device
    - since: Only cards created after this ISO timestamp
    - courses: Comma-separated course slugs to filter by (e.g., "sociology,ml-basics")
    """
    device_token = request.args.get("device_token")
    since = request.args.get("since")
    courses_param = request.args.get("courses")

    with get_db() as conn:
        with conn.cursor() as cur:
            # Build query based on parameters
            if device_token:
                # Return public cards + private cards for this device
                query = """
                    SELECT c.id, c.created_at, c.semantic_description, c.course_task_ref,
                           c.card_html, c.response_schema, c.visibility, c.device_token,
                           c.card_type, c.parent_response_id, c.generation_batch, co.slug as course_slug
                    FROM cards c
                    LEFT JOIN courses co ON c.course_id = co.id
                    WHERE (c.visibility = 'public' OR c.device_token = %s)
                """
                params = [device_token]
            else:
                # Return only public cards
                query = """
                    SELECT c.id, c.created_at, c.semantic_description, c.course_task_ref,
                           c.card_html, c.response_schema, c.visibility, c.device_token,
                           c.card_type, c.parent_response_id, c.generation_batch, co.slug as course_slug
                    FROM cards c
                    LEFT JOIN courses co ON c.course_id = co.id
                    WHERE c.visibility = 'public'
                """
                params = []

            # Filter by courses if provided
            if courses_param:
                course_slugs = [s.strip() for s in courses_param.split(",") if s.strip()]
                if course_slugs:
                    placeholders = ",".join(["%s"] * len(course_slugs))
                    query += f" AND co.slug IN ({placeholders})"
                    params.extend(course_slugs)

            # Filter by timestamp if provided
            if since:
                query += " AND c.created_at > %s"
                params.append(since)

            query += " ORDER BY c.created_at ASC"

            cur.execute(query, params)
            rows = cur.fetchall()

            cards = []
            for row in rows:
                cards.append({
                    "id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "semantic_description": row[2],
                    "course_task_ref": row[3],
                    "card_html": row[4],
                    "response_schema": row[5],
                    "visibility": row[6],
                    "device_token": row[7],
                    "card_type": row[8],
                    "parent_response_id": row[9],
                    "generation_batch": row[10],
                    "course_slug": row[11]
                })

            return jsonify({
                "cards": cards,
                "count": len(cards)
            })


@app.route("/api/cards/<int:card_id>")
def api_card(card_id):
    """Get a single card by ID (if public or owned by device)."""
    device_token = request.args.get("device_token")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, created_at, semantic_description, course_task_ref,
                       card_html, response_schema, visibility, device_token,
                       card_type, parent_response_id, generation_batch
                FROM cards
                WHERE id = %s
            """, (card_id,))
            row = cur.fetchone()

            if row is None:
                return jsonify({"error": "Card not found"}), 404

            # Check visibility
            visibility = row[6]
            card_device_token = row[7]

            if visibility != 'public' and card_device_token != device_token:
                return jsonify({"error": "Card not found"}), 404

            return jsonify({
                "card": {
                    "id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "semantic_description": row[2],
                    "course_task_ref": row[3],
                    "card_html": row[4],
                    "response_schema": row[5],
                    "visibility": row[6],
                    "device_token": row[7],
                    "card_type": row[8],
                    "parent_response_id": row[9],
                    "generation_batch": row[10]
                }
            })


@app.route("/api/cards/<int:card_id>/publish", methods=["POST"])
def api_publish_card(card_id):
    """Make a private card public."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    device_token = data.get("device_token")

    if not device_token:
        return jsonify({"error": "Missing device_token"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            # Only allow publishing if the card belongs to this device
            cur.execute("""
                UPDATE cards
                SET visibility = 'public'
                WHERE id = %s AND device_token = %s
            """, (card_id, device_token))

            if cur.rowcount == 0:
                return jsonify({"error": "Card not found or not owned by this device"}), 404

        conn.commit()

    return jsonify({"success": True, "message": "Card is now public"})


# ==========================================================
# SYNC API - Manual sync endpoint
# ==========================================================

@app.route("/api/sync", methods=["POST"])
def api_sync():
    """Main sync endpoint - upload responses, get new cards.

    Request body:
    {
        "device_token": "uuid",
        "responses": [
            {
                "card_id": 42,
                "response_content": {...},
                "responded_at": "ISO timestamp",
                "feedback": { "rating": 4, "comment": "..." }  // optional
            }
        ],
        "last_sync": "ISO timestamp" or null,
        "subscribed_courses": ["sociology", "ml-basics"]  // optional, filter cards
    }

    Response:
    {
        "success": true,
        "responses_received": 3,
        "new_cards": [...],
        "stats": {
            "total_responses": 47,
            "pending_evaluations": 3,
            "cards_available": 52
        }
    }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    device_token = data.get("device_token")
    responses = data.get("responses", [])
    last_sync = data.get("last_sync")
    subscribed_courses = data.get("subscribed_courses")  # List of course slugs

    if not device_token:
        return jsonify({"error": "Missing device_token"}), 400

    responses_received = 0

    with get_db() as conn:
        with conn.cursor() as cur:
            # Store each response
            for resp in responses:
                card_id = resp.get("card_id")
                response_content = resp.get("response_content")
                responded_at = resp.get("responded_at")
                feedback = resp.get("feedback")

                if not card_id or response_content is None:
                    continue

                # Insert response
                cur.execute("""
                    INSERT INTO responses (card_id, device_token, response_content, responded_at)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                """, (
                    card_id,
                    device_token,
                    json.dumps(response_content),
                    responded_at or datetime.utcnow().isoformat()
                ))
                response_id = cur.fetchone()[0]
                responses_received += 1

                # Insert feedback if provided
                if feedback and feedback.get("rating"):
                    cur.execute("""
                        INSERT INTO feedback (response_id, device_token, rating, comment)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        response_id,
                        device_token,
                        feedback.get("rating"),
                        feedback.get("comment")
                    ))

            # Build query for new cards with optional course filtering
            query = """
                SELECT c.id, c.created_at, c.semantic_description, c.course_task_ref,
                       c.card_html, c.response_schema, c.visibility, c.device_token,
                       c.card_type, c.parent_response_id, c.generation_batch, co.slug as course_slug
                FROM cards c
                LEFT JOIN courses co ON c.course_id = co.id
                WHERE (c.visibility = 'public' OR c.device_token = %s)
            """
            params = [device_token]

            # Filter by subscribed courses if provided
            if subscribed_courses and isinstance(subscribed_courses, list) and len(subscribed_courses) > 0:
                placeholders = ",".join(["%s"] * len(subscribed_courses))
                query += f" AND co.slug IN ({placeholders})"
                params.extend(subscribed_courses)

            # Filter by timestamp if provided
            if last_sync:
                query += " AND c.created_at > %s"
                params.append(last_sync)

            query += " ORDER BY c.created_at ASC"

            cur.execute(query, params)
            rows = cur.fetchall()

            new_cards = []
            for row in rows:
                new_cards.append({
                    "id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "semantic_description": row[2],
                    "course_task_ref": row[3],
                    "card_html": row[4],
                    "response_schema": row[5],
                    "visibility": row[6],
                    "device_token": row[7],
                    "card_type": row[8],
                    "parent_response_id": row[9],
                    "generation_batch": row[10],
                    "course_slug": row[11]
                })

            # Get stats for this device (filtered by subscribed courses if provided)
            if subscribed_courses and isinstance(subscribed_courses, list) and len(subscribed_courses) > 0:
                placeholders = ",".join(["%s"] * len(subscribed_courses))
                cur.execute(f"""
                    SELECT
                        (SELECT COUNT(*) FROM responses WHERE device_token = %s) as total_responses,
                        (SELECT COUNT(*) FROM responses WHERE device_token = %s AND evaluated = FALSE) as pending_evaluations,
                        (SELECT COUNT(*) FROM cards c
                         LEFT JOIN courses co ON c.course_id = co.id
                         WHERE (c.visibility = 'public' OR c.device_token = %s)
                           AND co.slug IN ({placeholders})) as cards_available
                """, (device_token, device_token, device_token, *subscribed_courses))
            else:
                cur.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM responses WHERE device_token = %s) as total_responses,
                        (SELECT COUNT(*) FROM responses WHERE device_token = %s AND evaluated = FALSE) as pending_evaluations,
                        (SELECT COUNT(*) FROM cards WHERE visibility = 'public' OR device_token = %s) as cards_available
                """, (device_token, device_token, device_token))
            stats_row = cur.fetchone()

        conn.commit()

    return jsonify({
        "success": True,
        "responses_received": responses_received,
        "new_cards": new_cards,
        "stats": {
            "total_responses": stats_row[0],
            "pending_evaluations": stats_row[1],
            "cards_available": stats_row[2]
        }
    })


# ==========================================================
# TASK PAGES API - Standalone learning content
# ==========================================================

@app.route("/api/task-pages")
def api_task_pages():
    """List task pages with optional filters.

    Query params:
    - course: Filter by course slug
    - device_token: Include status for this device (via header or param)
    """
    course_slug = request.args.get("course")
    device_token = request.headers.get("X-Device-Token") or request.args.get("device_token")

    with get_db() as conn:
        with conn.cursor() as cur:
            # Build query
            query = """
                SELECT tp.id, tp.created_at, tp.updated_at, tp.title, tp.description,
                       tp.course_id, tp.topics, tp.estimated_duration_minutes,
                       tp.difficulty, c.slug as course_slug
                FROM task_pages tp
                LEFT JOIN courses c ON tp.course_id = c.id
                WHERE 1=1
            """
            params = []

            if course_slug:
                query += " AND c.slug = %s"
                params.append(course_slug)

            query += " ORDER BY tp.created_at DESC"

            cur.execute(query, params)
            rows = cur.fetchall()

            task_pages = []
            for row in rows:
                page = {
                    "id": row[0],
                    "created_at": row[1].isoformat() if row[1] else None,
                    "updated_at": row[2].isoformat() if row[2] else None,
                    "title": row[3],
                    "description": row[4],
                    "course_id": row[5],
                    "topics": row[6] or [],
                    "estimated_duration_minutes": row[7],
                    "difficulty": row[8],
                    "course_slug": row[9]
                }

                # Get status for device if token provided
                if device_token:
                    cur.execute("""
                        SELECT status, started_at, completed_at, updated_at
                        FROM task_page_statuses
                        WHERE task_page_id = %s AND device_token = %s
                    """, (row[0], device_token))
                    status_row = cur.fetchone()
                    if status_row:
                        page["status"] = {
                            "status": status_row[0],
                            "started_at": status_row[1].isoformat() if status_row[1] else None,
                            "completed_at": status_row[2].isoformat() if status_row[2] else None,
                            "updated_at": status_row[3].isoformat() if status_row[3] else None
                        }
                    else:
                        page["status"] = {"status": "not_started"}

                task_pages.append(page)

            return jsonify({
                "task_pages": task_pages,
                "count": len(task_pages)
            })


@app.route("/api/task-pages/<task_page_id>")
def api_task_page(task_page_id):
    """Get a single task page with status.

    Query params / Headers:
    - device_token / X-Device-Token: Get status for this device
    """
    device_token = request.headers.get("X-Device-Token") or request.args.get("device_token")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT tp.id, tp.created_at, tp.updated_at, tp.title, tp.description,
                       tp.page_html, tp.course_id, tp.topics, tp.estimated_duration_minutes,
                       tp.difficulty, tp.generation_batch, c.slug as course_slug
                FROM task_pages tp
                LEFT JOIN courses c ON tp.course_id = c.id
                WHERE tp.id = %s
            """, (task_page_id,))
            row = cur.fetchone()

            if not row:
                return jsonify({"error": "Task page not found"}), 404

            page = {
                "id": row[0],
                "created_at": row[1].isoformat() if row[1] else None,
                "updated_at": row[2].isoformat() if row[2] else None,
                "title": row[3],
                "description": row[4],
                "has_html": bool(row[5]),  # Don't include full HTML here
                "course_id": row[6],
                "topics": row[7] or [],
                "estimated_duration_minutes": row[8],
                "difficulty": row[9],
                "generation_batch": row[10],
                "course_slug": row[11]
            }

            # Get status for device if token provided
            if device_token:
                cur.execute("""
                    SELECT status, started_at, completed_at, updated_at, notes
                    FROM task_page_statuses
                    WHERE task_page_id = %s AND device_token = %s
                """, (task_page_id, device_token))
                status_row = cur.fetchone()
                if status_row:
                    page["status"] = {
                        "status": status_row[0],
                        "started_at": status_row[1].isoformat() if status_row[1] else None,
                        "completed_at": status_row[2].isoformat() if status_row[2] else None,
                        "updated_at": status_row[3].isoformat() if status_row[3] else None,
                        "notes": status_row[4]
                    }
                else:
                    page["status"] = {"status": "not_started"}

                # Check if evaluation exists
                cur.execute("""
                    SELECT COUNT(*) FROM task_page_responses
                    WHERE task_page_id = %s AND device_token = %s AND evaluation IS NOT NULL
                """, (task_page_id, device_token))
                page["has_evaluation"] = cur.fetchone()[0] > 0

            return jsonify(page)


@app.route("/api/task-pages/<task_page_id>/html")
def api_task_page_html(task_page_id):
    """Get raw HTML for a task page (for iframe rendering).

    This returns just the HTML content, not JSON.
    The PWA will inject device_token before rendering.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT page_html FROM task_pages WHERE id = %s
            """, (task_page_id,))
            row = cur.fetchone()

            if not row:
                return "Task page not found", 404

            return row[0], 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/api/task-pages/<task_page_id>/status", methods=["GET", "POST"])
def api_task_page_status(task_page_id):
    """Get or update status for a task page.

    GET: Returns current status for device
    POST: Updates status

    Headers:
    - X-Device-Token: Required

    POST body:
    {
        "status": "not_started" | "draft" | "in_progress" | "completed",
        "notes": "optional notes"
    }
    """
    device_token = request.headers.get("X-Device-Token")
    if not device_token:
        return jsonify({"error": "Missing X-Device-Token header"}), 401

    with get_db() as conn:
        with conn.cursor() as cur:
            # Verify task page exists
            cur.execute("SELECT id FROM task_pages WHERE id = %s", (task_page_id,))
            if not cur.fetchone():
                return jsonify({"error": "Task page not found"}), 404

            if request.method == "GET":
                cur.execute("""
                    SELECT status, started_at, completed_at, updated_at, notes
                    FROM task_page_statuses
                    WHERE task_page_id = %s AND device_token = %s
                """, (task_page_id, device_token))
                row = cur.fetchone()

                if row:
                    return jsonify({
                        "status": row[0],
                        "started_at": row[1].isoformat() if row[1] else None,
                        "completed_at": row[2].isoformat() if row[2] else None,
                        "updated_at": row[3].isoformat() if row[3] else None,
                        "notes": row[4]
                    })
                else:
                    return jsonify({"status": "not_started"})

            else:  # POST
                data = request.get_json()
                if not data:
                    return jsonify({"error": "No data provided"}), 400

                new_status = data.get("status")
                notes = data.get("notes")

                valid_statuses = ["not_started", "draft", "in_progress", "completed"]
                if new_status and new_status not in valid_statuses:
                    return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

                # Check if status record exists
                cur.execute("""
                    SELECT id, status FROM task_page_statuses
                    WHERE task_page_id = %s AND device_token = %s
                """, (task_page_id, device_token))
                existing = cur.fetchone()

                now = datetime.utcnow()

                if existing:
                    # Update existing status
                    update_fields = ["updated_at = %s"]
                    update_params = [now]

                    if new_status:
                        update_fields.append("status = %s")
                        update_params.append(new_status)

                        # Set timestamps based on status transitions
                        old_status = existing[1]
                        if new_status in ["draft", "in_progress"] and old_status == "not_started":
                            update_fields.append("started_at = %s")
                            update_params.append(now)
                        if new_status == "completed":
                            update_fields.append("completed_at = %s")
                            update_params.append(now)

                    if notes is not None:
                        update_fields.append("notes = %s")
                        update_params.append(notes)

                    update_params.append(existing[0])
                    cur.execute(f"""
                        UPDATE task_page_statuses
                        SET {", ".join(update_fields)}
                        WHERE id = %s
                    """, update_params)
                else:
                    # Create new status record
                    started_at = now if new_status in ["draft", "in_progress", "completed"] else None
                    completed_at = now if new_status == "completed" else None

                    cur.execute("""
                        INSERT INTO task_page_statuses
                        (task_page_id, device_token, status, started_at, completed_at, updated_at, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        task_page_id,
                        device_token,
                        new_status or "not_started",
                        started_at,
                        completed_at,
                        now,
                        notes
                    ))

                conn.commit()

                # Return updated status
                cur.execute("""
                    SELECT status, started_at, completed_at, updated_at, notes
                    FROM task_page_statuses
                    WHERE task_page_id = %s AND device_token = %s
                """, (task_page_id, device_token))
                row = cur.fetchone()

                return jsonify({
                    "success": True,
                    "status": row[0],
                    "started_at": row[1].isoformat() if row[1] else None,
                    "completed_at": row[2].isoformat() if row[2] else None,
                    "updated_at": row[3].isoformat() if row[3] else None,
                    "notes": row[4]
                })


# ==========================================================
# LEGACY API - For backwards compatibility during transition
# These endpoints will be removed after full migration to local-first
# ==========================================================

@app.route("/api/next-card")
def api_next_card():
    """LEGACY: Get the next card. Redirects to /api/cards in local-first model."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get first public card (simple version for backwards compat)
            cur.execute("""
                SELECT id, semantic_description, card_html, response_schema
                FROM cards
                WHERE visibility = 'public'
                ORDER BY created_at ASC
                LIMIT 1
            """)
            card = cur.fetchone()

            if card is None:
                return jsonify({"card": None, "message": "Keine weiteren Karten verfügbar"})

            # Get basic stats
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM responses WHERE DATE(responded_at) = CURRENT_DATE) as today_completed,
                    (SELECT COUNT(*) FROM cards WHERE visibility = 'public') as remaining
            """)
            stats = cur.fetchone()

            return jsonify({
                "card": {
                    "id": card[0],
                    "semantic_description": card[1],
                    "card_html": card[2],
                    "response_schema": card[3],
                    "notes": None  # Notes now live in IndexedDB
                },
                "progress": {
                    "today_completed": stats[0],
                    "remaining": stats[1]
                }
            })


@app.route("/api/response", methods=["POST"])
def api_response():
    """LEGACY: Record a response. Use /api/sync instead."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    card_id = data.get("card_id")
    response_content = data.get("response_content")
    device_token = data.get("device_token", "legacy-anonymous")

    if not card_id or response_content is None:
        return jsonify({"error": "Missing card_id or response_content"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO responses (card_id, device_token, response_content)
                   VALUES (%s, %s, %s)
                   RETURNING id""",
                (card_id, device_token, json.dumps(response_content))
            )
            response_id = cur.fetchone()[0]
        conn.commit()

    return jsonify({
        "success": True,
        "response_id": response_id,
        "message": "Aufgezeichnet"
    })


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """LEGACY: Record feedback. Use /api/sync instead."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    response_id = data.get("response_id")
    rating = data.get("rating")
    comment = data.get("comment", "")
    device_token = data.get("device_token", "legacy-anonymous")

    if not response_id or rating is None:
        return jsonify({"error": "Missing response_id or rating"}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be integer 1-5"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO feedback (response_id, device_token, rating, comment)
                VALUES (%s, %s, %s, %s)
            """, (response_id, device_token, rating, comment.strip() if comment else None))
        conn.commit()

    return jsonify({"success": True, "message": "Feedback gespeichert"})


@app.route("/api/skip", methods=["POST"])
def api_skip():
    """LEGACY: Skip is now handled client-side in IndexedDB."""
    return jsonify({"success": True, "message": "OK (handled client-side)"})


@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    """LEGACY: Scheduling is now handled client-side in IndexedDB."""
    return jsonify({"success": True, "message": "OK (handled client-side)"})


@app.route("/api/card/<int:card_id>/notes", methods=["GET", "POST"])
def api_card_notes(card_id):
    """LEGACY: Notes are now stored client-side in IndexedDB."""
    if request.method == "GET":
        return jsonify({"notes": None, "message": "Notes are stored locally"})
    else:
        return jsonify({"success": True, "message": "OK (stored client-side)"})


@app.route("/api/stats")
def api_stats():
    """Get learning statistics."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM cards WHERE visibility = 'public') as public_cards,
                    (SELECT COUNT(*) FROM cards WHERE visibility = 'private') as private_cards,
                    (SELECT COUNT(*) FROM responses) as total_responses,
                    (SELECT COUNT(*) FROM responses WHERE DATE(responded_at) = CURRENT_DATE) as today_responses,
                    (SELECT COUNT(*) FROM responses WHERE evaluated = FALSE) as pending_evaluations
            """)
            stats = cur.fetchone()

    return jsonify({
        "public_cards": stats[0],
        "private_cards": stats[1],
        "total_responses": stats[2],
        "today_responses": stats[3],
        "pending_evaluations": stats[4]
    })


# ==========================================================
# UTILITY ENDPOINTS
# ==========================================================

@app.route("/test-card")
def test_card():
    """Test harness for card HTML snippets."""
    return render_template("test_card.html")


@app.route("/health")
def health():
    """Health check endpoint."""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        return "OK", 200
    except Exception as e:
        return f"DB Error: {e}", 500


# ==========================================================
# TEST ENDPOINTS - Staging only
# ==========================================================

def is_staging():
    """Check if running on staging environment."""
    fly_app = os.getenv("FLY_APP_NAME", "")
    return "staging" in fly_app or os.getenv("ALLOW_TEST_ENDPOINTS") == "true"


@app.route("/api/test/reset-client")
def api_test_reset_client():
    """Returns instructions for clearing client-side state."""
    if not is_staging():
        return jsonify({"error": "Not available"}), 404

    return jsonify({
        "success": True,
        "instructions": [
            "Open DevTools (F12 or Cmd+Option+I)",
            "Go to Application tab",
            "Click 'Clear site data' in Storage section",
            "Or: IndexedDB → right-click 'sociology-learning' → Delete database",
            "Reload the page"
        ],
        "note": "This endpoint cannot clear client-side storage directly - it must be done in the browser."
    })


@app.route("/api/test/seed-cards")
def api_test_seed_cards():
    """Add test cards for testing purposes."""
    if not is_staging():
        return jsonify({"error": "Not available"}), 404

    count = request.args.get("count", 3, type=int)
    count = min(count, 10)  # Limit to 10 cards

    test_cards = [
        {
            "semantic_description": "Test card: Multiple choice question about sociology",
            "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Testfrage</p>
        <h2 class="text-lg font-semibold mb-4">Was ist ein soziales System?</h2>
        <div class="space-y-2">
            <label class="flex items-center p-3 border rounded-lg cursor-pointer" :class="selected === 'a' ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'">
                <input type="radio" x-model="selected" value="a" class="mr-3"> Ein Computer-Netzwerk
            </label>
            <label class="flex items-center p-3 border rounded-lg cursor-pointer" :class="selected === 'b' ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'">
                <input type="radio" x-model="selected" value="b" class="mr-3"> Eine Gruppe von Menschen mit Interaktionen
            </label>
            <label class="flex items-center p-3 border rounded-lg cursor-pointer" :class="selected === 'c' ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'">
                <input type="radio" x-model="selected" value="c" class="mr-3"> Ein politisches Gebilde
            </label>
        </div>
        <button @click="submitResponse({ answer: selected })" :disabled="!selected || submitting"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>''',
            "response_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
        },
        {
            "semantic_description": "Test card: Free text question about norms",
            "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Testfrage</p>
        <h2 class="text-lg font-semibold mb-4">Erkläre den Begriff "soziale Norm" in eigenen Worten.</h2>
        <textarea x-model="answer" class="w-full p-3 border border-gray-300 rounded-lg" rows="4" placeholder="Deine Antwort..."></textarea>
        <button @click="submitResponse({ answer })" :disabled="answer.trim().length < 10 || submitting"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>''',
            "response_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
        },
        {
            "semantic_description": "Test card: Self-assessment question",
            "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ confidence: 3 }">
        <p class="text-gray-600 text-sm mb-2">Selbsteinschätzung</p>
        <h2 class="text-lg font-semibold mb-4">Wie gut verstehst du den Unterschied zwischen Rolle und Status?</h2>
        <div class="flex justify-between mb-4">
            <template x-for="i in 5">
                <button @click="confidence = i" class="w-12 h-12 rounded-full border-2 text-lg font-semibold"
                        :class="confidence === i ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-gray-300'">
                    <span x-text="i"></span>
                </button>
            </template>
        </div>
        <p class="text-sm text-gray-500 text-center mb-4">1 = gar nicht, 5 = sehr gut</p>
        <button @click="submitResponse({ confidence })" :disabled="submitting"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>''',
            "response_schema": {"type": "object", "properties": {"confidence": {"type": "integer"}}, "required": ["confidence"]}
        }
    ]

    cards_added = 0
    with get_db() as conn:
        with conn.cursor() as cur:
            for i in range(count):
                card = test_cards[i % len(test_cards)]
                cur.execute(
                    """INSERT INTO cards (semantic_description, card_html, response_schema, visibility, card_type)
                       VALUES (%s, %s, %s, 'public', 'learning')""",
                    (f"{card['semantic_description']} (test #{i+1})", card['card_html'], json.dumps(card['response_schema']))
                )
                cards_added += 1
        conn.commit()

    return jsonify({
        "success": True,
        "cards_added": cards_added,
        "message": f"Added {cards_added} test cards"
    })


@app.route("/api/test/clear-responses")
def api_test_clear_responses():
    """Clear responses for a device token."""
    if not is_staging():
        return jsonify({"error": "Not available"}), 404

    device_token = request.args.get("device_token")
    if not device_token:
        return jsonify({"error": "Missing device_token parameter"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            # Delete feedback first (foreign key)
            cur.execute("DELETE FROM feedback WHERE device_token = %s", (device_token,))
            # Delete responses
            cur.execute("DELETE FROM responses WHERE device_token = %s", (device_token,))
            deleted = cur.rowcount
        conn.commit()

    return jsonify({
        "success": True,
        "responses_deleted": deleted
    })


@app.route("/api/test/db-state")
def api_test_db_state():
    """Get current database state for debugging."""
    if not is_staging():
        return jsonify({"error": "Not available"}), 404

    device_token = request.args.get("device_token")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM cards")
            cards_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM responses")
            responses_count = cur.fetchone()[0]

            device_responses = 0
            if device_token:
                cur.execute("SELECT COUNT(*) FROM responses WHERE device_token = %s", (device_token,))
                device_responses = cur.fetchone()[0]

    return jsonify({
        "cards_count": cards_count,
        "responses_count": responses_count,
        "device_responses": device_responses
    })


# Template filter to mark HTML as safe
@app.template_filter('safe_html')
def safe_html(s):
    return Markup(s)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
