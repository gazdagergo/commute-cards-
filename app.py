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
            # Get the oldest active card that hasn't been completed or skipped
            cur.execute("""
                SELECT id, semantic_description, card_html, response_schema
                FROM cards
                WHERE status = 'active'
                ORDER BY created_at ASC
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
            # Verify the card exists and is active
            cur.execute("SELECT id, status FROM cards WHERE id = %s", (card_id,))
            card = cur.fetchone()

            if card is None:
                return jsonify({"error": "Card not found"}), 404

            if card[1] != 'active':
                return jsonify({"error": "Card is not active"}), 400

            # Insert the response
            cur.execute(
                """INSERT INTO responses (card_id, response_content)
                   VALUES (%s, %s)
                   RETURNING id""",
                (card_id, json.dumps(response_content))
            )
            response_id = cur.fetchone()[0]

            # Mark the card as completed
            cur.execute(
                "UPDATE cards SET status = 'completed' WHERE id = %s",
                (card_id,)
            )

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
                "UPDATE cards SET status = 'skipped' WHERE id = %s AND status = 'active'",
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