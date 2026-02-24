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

@app.route("/api/cards")
def api_cards():
    """Get cards - public cards and optionally device-specific private cards.

    Query params:
    - device_token: Include private cards for this device
    - since: Only cards created after this ISO timestamp
    """
    device_token = request.args.get("device_token")
    since = request.args.get("since")

    with get_db() as conn:
        with conn.cursor() as cur:
            # Build query based on parameters
            if device_token:
                # Return public cards + private cards for this device
                query = """
                    SELECT id, created_at, semantic_description, course_task_ref,
                           card_html, response_schema, visibility, device_token,
                           card_type, parent_response_id, generation_batch
                    FROM cards
                    WHERE visibility = 'public'
                       OR device_token = %s
                """
                params = [device_token]
            else:
                # Return only public cards
                query = """
                    SELECT id, created_at, semantic_description, course_task_ref,
                           card_html, response_schema, visibility, device_token,
                           card_type, parent_response_id, generation_batch
                    FROM cards
                    WHERE visibility = 'public'
                """
                params = []

            # Filter by timestamp if provided
            if since:
                query += " AND created_at > %s"
                params.append(since)

            query += " ORDER BY created_at ASC"

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
                    "generation_batch": row[10]
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
        "last_sync": "ISO timestamp" or null
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

            # Get new cards since last sync
            if last_sync:
                cur.execute("""
                    SELECT id, created_at, semantic_description, course_task_ref,
                           card_html, response_schema, visibility, device_token,
                           card_type, parent_response_id, generation_batch
                    FROM cards
                    WHERE (visibility = 'public' OR device_token = %s)
                      AND created_at > %s
                    ORDER BY created_at ASC
                """, (device_token, last_sync))
            else:
                # First sync - get all available cards
                cur.execute("""
                    SELECT id, created_at, semantic_description, course_task_ref,
                           card_html, response_schema, visibility, device_token,
                           card_type, parent_response_id, generation_batch
                    FROM cards
                    WHERE visibility = 'public' OR device_token = %s
                    ORDER BY created_at ASC
                """, (device_token,))

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
                    "generation_batch": row[10]
                })

            # Get stats for this device
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


# Template filter to mark HTML as safe
@app.template_filter('safe_html')
def safe_html(s):
    return Markup(s)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
