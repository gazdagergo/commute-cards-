import os
import json
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
    with get_db() as conn:
        with conn.cursor() as cur:
            # Cards table - stores learning cards with their HTML snippets
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cards (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    semantic_description TEXT NOT NULL,
                    course_task_ref VARCHAR(255),
                    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'skipped')),
                    card_html TEXT NOT NULL,
                    response_schema JSONB NOT NULL
                )
            """)

            # Responses table - stores user responses to cards
            cur.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id SERIAL PRIMARY KEY,
                    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
                    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response_content JSONB NOT NULL,
                    evaluation JSONB
                )
            """)

            # Create index for faster queries on active cards
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_cards_status ON cards(status)
            """)

            # Create index for faster queries on unevaluated responses
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_responses_evaluation ON responses(evaluation) WHERE evaluation IS NULL
            """)

            # Migration: Add feedback column to responses table
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'responses' AND column_name = 'feedback'
                    ) THEN
                        ALTER TABLE responses ADD COLUMN feedback JSONB;
                    END IF;
                END $$;
            """)

            # Migration: Add scheduled_for column to cards table
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'scheduled_for'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN scheduled_for DATE;
                    END IF;
                END $$;
            """)

            # Migration: Update status CHECK constraint to allow 'scheduled'
            cur.execute("""
                DO $$
                BEGIN
                    ALTER TABLE cards DROP CONSTRAINT IF EXISTS cards_status_check;
                    ALTER TABLE cards ADD CONSTRAINT cards_status_check
                        CHECK (status IN ('active', 'completed', 'skipped', 'scheduled'));
                EXCEPTION
                    WHEN others THEN NULL;
                END $$;
            """)

            # Migration: Add queued_at column for queue ordering
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'cards' AND column_name = 'queued_at'
                    ) THEN
                        ALTER TABLE cards ADD COLUMN queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                        UPDATE cards SET queued_at = created_at WHERE queued_at IS NULL;
                    END IF;
                END $$;
            """)

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
                    """INSERT INTO cards (semantic_description, status, card_html, response_schema)
                       VALUES (%s, %s, %s, %s)""",
                    (
                        "Define the concept of socialization (Sozialisation) - fundamental sociology term",
                        "active",
                        sample_card_html,
                        sample_schema
                    )
                )
        conn.commit()


@app.route("/")
def index():
    """Main app view - renders the card interface."""
    return render_template("index.html")


@app.route("/api/next-card")
def api_next_card():
    """Get the next active card to display."""
    with get_db() as conn:
        with conn.cursor() as cur:
            # Get active cards OR scheduled cards that are due today or earlier
            # Order by queued_at so "repeat today" cards go to end of queue
            cur.execute("""
                SELECT id, semantic_description, card_html, response_schema
                FROM cards
                WHERE status = 'active'
                   OR (status = 'scheduled' AND scheduled_for <= CURRENT_DATE)
                ORDER BY
                    CASE WHEN status = 'scheduled' THEN 0 ELSE 1 END,
                    scheduled_for ASC NULLS LAST,
                    queued_at ASC NULLS FIRST
                LIMIT 1
            """)
            card = cur.fetchone()

            if card is None:
                return jsonify({"card": None, "message": "Keine weiteren Karten verfügbar"})

            # Get daily progress stats
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM responses WHERE DATE(responded_at) = CURRENT_DATE) as today_completed,
                    (SELECT COUNT(*) FROM cards WHERE status = 'active') as remaining
            """)
            stats = cur.fetchone()

            return jsonify({
                "card": {
                    "id": card[0],
                    "semantic_description": card[1],
                    "card_html": card[2],
                    "response_schema": card[3]
                },
                "progress": {
                    "today_completed": stats[0],
                    "remaining": stats[1]
                }
            })


@app.route("/api/response", methods=["POST"])
def api_response():
    """Record a response to a card."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    card_id = data.get("card_id")
    response_content = data.get("response_content")

    if not card_id or response_content is None:
        return jsonify({"error": "Missing card_id or response_content"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            # Verify the card exists and is active or due scheduled
            cur.execute("""
                SELECT id, status, scheduled_for FROM cards WHERE id = %s
            """, (card_id,))
            card = cur.fetchone()

            if card is None:
                return jsonify({"error": "Card not found"}), 404

            status = card[1]
            scheduled_for = card[2]
            is_due = status == 'active' or (status == 'scheduled' and scheduled_for is not None)

            if not is_due:
                return jsonify({"error": "Card is not active"}), 400

            # Insert the response (card status will be updated via /api/schedule)
            cur.execute(
                """INSERT INTO responses (card_id, response_content)
                   VALUES (%s, %s)
                   RETURNING id""",
                (card_id, json.dumps(response_content))
            )
            response_id = cur.fetchone()[0]

        conn.commit()

    return jsonify({
        "success": True,
        "response_id": response_id,
        "message": "Aufgezeichnet"
    })


@app.route("/api/skip", methods=["POST"])
def api_skip():
    """Skip a card."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    card_id = data.get("card_id")

    if not card_id:
        return jsonify({"error": "Missing card_id"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """UPDATE cards SET status = 'skipped', scheduled_for = NULL
                   WHERE id = %s AND (status = 'active' OR status = 'scheduled')""",
                (card_id,)
            )
            if cur.rowcount == 0:
                return jsonify({"error": "Card not found or not active"}), 404

        conn.commit()

    return jsonify({"success": True, "message": "Übersprungen"})


@app.route("/api/stats")
def api_stats():
    """Get learning statistics."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM cards WHERE status = 'active') as active_cards,
                    (SELECT COUNT(*) FROM cards WHERE status = 'completed') as completed_cards,
                    (SELECT COUNT(*) FROM cards WHERE status = 'skipped') as skipped_cards,
                    (SELECT COUNT(*) FROM responses WHERE DATE(responded_at) = CURRENT_DATE) as today_responses,
                    (SELECT COUNT(*) FROM responses WHERE evaluation IS NULL) as pending_evaluations
            """)
            stats = cur.fetchone()

    return jsonify({
        "active_cards": stats[0],
        "completed_cards": stats[1],
        "skipped_cards": stats[2],
        "today_responses": stats[3],
        "pending_evaluations": stats[4]
    })


@app.route("/api/feedback", methods=["POST"])
def api_feedback():
    """Record feedback for a response."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    response_id = data.get("response_id")
    rating = data.get("rating")  # 1-5 stars
    comment = data.get("comment", "")  # optional text feedback

    if not response_id or rating is None:
        return jsonify({"error": "Missing response_id or rating"}), 400

    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"error": "Rating must be integer 1-5"}), 400

    feedback = {
        "rating": rating,
        "comment": comment.strip() if comment else None
    }

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE responses SET feedback = %s WHERE id = %s",
                (json.dumps(feedback), response_id)
            )
            if cur.rowcount == 0:
                return jsonify({"error": "Response not found"}), 404

        conn.commit()

    return jsonify({"success": True, "message": "Feedback gespeichert"})


@app.route("/api/schedule", methods=["POST"])
def api_schedule():
    """Schedule a card for repetition."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    card_id = data.get("card_id")
    schedule_type = data.get("schedule_type")  # 'today', 'days', 'never'
    days = data.get("days")  # number of days (only for 'days' type)

    if not card_id or not schedule_type:
        return jsonify({"error": "Missing card_id or schedule_type"}), 400

    if schedule_type not in ['today', 'days', 'never']:
        return jsonify({"error": "Invalid schedule_type"}), 400

    if schedule_type == 'days':
        if not isinstance(days, int) or days < 1:
            return jsonify({"error": "Days must be a positive integer"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            if schedule_type == 'today':
                # Keep card active, move to end of queue
                cur.execute(
                    "UPDATE cards SET status = 'active', scheduled_for = NULL, queued_at = NOW() WHERE id = %s",
                    (card_id,)
                )
            elif schedule_type == 'days':
                # Schedule for future date
                cur.execute(
                    "UPDATE cards SET status = 'scheduled', scheduled_for = CURRENT_DATE + %s WHERE id = %s",
                    (days, card_id)
                )
            elif schedule_type == 'never':
                # Mark as completed
                cur.execute(
                    "UPDATE cards SET status = 'completed', scheduled_for = NULL WHERE id = %s",
                    (card_id,)
                )

            if cur.rowcount == 0:
                return jsonify({"error": "Card not found"}), 404

        conn.commit()

    return jsonify({"success": True, "message": "Zeitplan gespeichert"})


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