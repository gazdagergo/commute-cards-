import os
from flask import Flask, render_template, request, redirect, url_for
import psycopg
import markdown

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/chinese_learning_pwa")


def get_db():
    """Get a database connection."""
    return psycopg.connect(DATABASE_URL)


def init_db():
    """Create tables if they don't exist and seed test data."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stories (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flashcards (
                    id SERIAL PRIMARY KEY,
                    chinese VARCHAR(50) NOT NULL,
                    english VARCHAR(255) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flashcard_stories (
                    flashcard_id INTEGER REFERENCES flashcards(id) ON DELETE CASCADE,
                    story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
                    PRIMARY KEY (flashcard_id, story_id)
                )
            """)
            # New tables for story slices
            cur.execute("""
                CREATE TABLE IF NOT EXISTS story_slices (
                    id SERIAL PRIMARY KEY,
                    story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
                    slice_order INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    image_url VARCHAR(512),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(story_id, slice_order)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flashcard_slices (
                    flashcard_id INTEGER REFERENCES flashcards(id) ON DELETE CASCADE,
                    slice_id INTEGER REFERENCES story_slices(id) ON DELETE CASCADE,
                    PRIMARY KEY (flashcard_id, slice_id)
                )
            """)

            # Migration: create slices for existing stories that don't have any
            cur.execute("""
                INSERT INTO story_slices (story_id, slice_order, text)
                SELECT s.id, 1, s.text
                FROM stories s
                WHERE NOT EXISTS (
                    SELECT 1 FROM story_slices ss WHERE ss.story_id = s.id
                )
            """)

            # Migration: migrate flashcard_stories links to flashcard_slices
            cur.execute("""
                INSERT INTO flashcard_slices (flashcard_id, slice_id)
                SELECT fs.flashcard_id, ss.id
                FROM flashcard_stories fs
                JOIN story_slices ss ON ss.story_id = fs.story_id AND ss.slice_order = 1
                WHERE NOT EXISTS (
                    SELECT 1 FROM flashcard_slices fsl
                    WHERE fsl.flashcard_id = fs.flashcard_id AND fsl.slice_id = ss.id
                )
            """)

            cur.execute("SELECT COUNT(*) FROM stories")
            if cur.fetchone()[0] == 0:
                cur.execute(
                    "INSERT INTO stories (title, text) VALUES (%s, %s) RETURNING id",
                    ("测试故事", "这是一个测试故事。它用来验证数据库连接是否正常工作。希望一切顺利！")
                )
                story_id = cur.fetchone()[0]
                cur.execute(
                    "INSERT INTO story_slices (story_id, slice_order, text) VALUES (%s, %s, %s)",
                    (story_id, 1, "这是一个测试故事。它用来验证数据库连接是否正常工作。希望一切顺利！")
                )
        conn.commit()


@app.route("/")
def index():
    """List all stories."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, created_at FROM stories ORDER BY created_at DESC")
            stories = cur.fetchall()
    return render_template("index.html", stories=stories)


@app.route("/story/<int:story_id>")
@app.route("/story/<int:story_id>/slice/<int:slice_num>")
def story(story_id, slice_num=1):
    """Show a single story with slice pagination."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title, text, created_at FROM stories WHERE id = %s", (story_id,))
            story = cur.fetchone()
            if story is None:
                return "Story not found", 404

            # Get all slices for this story
            cur.execute("""
                SELECT id, slice_order, text, image_url
                FROM story_slices
                WHERE story_id = %s
                ORDER BY slice_order
            """, (story_id,))
            slices = cur.fetchall()

            # Get total slice count
            total_slices = len(slices)

            # Validate slice_num
            if slice_num < 1 or slice_num > total_slices:
                slice_num = 1

            # Get flashcards for ALL slices (for client-side rendering)
            slices_data = []
            for s in slices:
                cur.execute("""
                    SELECT f.id, f.chinese, f.english
                    FROM flashcards f
                    JOIN flashcard_slices fs ON f.id = fs.flashcard_id
                    WHERE fs.slice_id = %s
                    ORDER BY f.chinese
                """, (s[0],))
                flashcards = cur.fetchall()
                slices_data.append({
                    'id': s[0],
                    'order': s[1],
                    'text': s[2],
                    'image_url': s[3],
                    'flashcards': [{'id': f[0], 'chinese': f[1], 'english': f[2]} for f in flashcards]
                })

    return render_template("story.html",
                           story=story,
                           slices_data=slices_data,
                           initial_slice_num=slice_num,
                           total_slices=total_slices)


@app.route("/story/<int:story_id>/slice/add", methods=["GET", "POST"])
def slice_add(story_id):
    """Add a new slice to a story."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM stories WHERE id = %s", (story_id,))
            story = cur.fetchone()
            if story is None:
                return "Story not found", 404

            # Get the next slice order
            cur.execute("""
                SELECT COALESCE(MAX(slice_order), 0) + 1
                FROM story_slices WHERE story_id = %s
            """, (story_id,))
            next_order = cur.fetchone()[0]

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        image_url = request.form.get("image_url", "").strip() or None
        if text:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO story_slices (story_id, slice_order, text, image_url)
                        VALUES (%s, %s, %s, %s)
                    """, (story_id, next_order, text, image_url))
                conn.commit()
            return redirect(url_for("story", story_id=story_id, slice_num=next_order))
    return render_template("slice_form.html", story=story, slice=None, next_order=next_order)


@app.route("/story/<int:story_id>/slice/<int:slice_num>/edit", methods=["GET", "POST"])
def slice_edit(story_id, slice_num):
    """Edit a slice."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, title FROM stories WHERE id = %s", (story_id,))
            story = cur.fetchone()
            if story is None:
                return "Story not found", 404

            cur.execute("""
                SELECT id, slice_order, text, image_url
                FROM story_slices
                WHERE story_id = %s AND slice_order = %s
            """, (story_id, slice_num))
            slice_data = cur.fetchone()
            if slice_data is None:
                return "Slice not found", 404

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        image_url = request.form.get("image_url", "").strip() or None
        if text:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE story_slices
                        SET text = %s, image_url = %s
                        WHERE id = %s
                    """, (text, image_url, slice_data[0]))
                conn.commit()
            return redirect(url_for("story", story_id=story_id, slice_num=slice_num))
    return render_template("slice_form.html", story=story, slice=slice_data, next_order=None)


@app.route("/add", methods=["GET", "POST"])
def add():
    """Add a new story."""
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        text = request.form.get("text", "").strip()
        if title and text:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO stories (title, text) VALUES (%s, %s) RETURNING id",
                        (title, text)
                    )
                    story_id = cur.fetchone()[0]
                    # Create the first slice automatically
                    cur.execute(
                        "INSERT INTO story_slices (story_id, slice_order, text) VALUES (%s, %s, %s)",
                        (story_id, 1, text)
                    )
                conn.commit()
            return redirect(url_for("index"))
    return render_template("add.html")


@app.route("/flashcards")
def flashcards():
    """List all flashcards."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, chinese, english, description, created_at FROM flashcards ORDER BY created_at DESC")
            cards = cur.fetchall()
    return render_template("flashcards.html", cards=cards)


@app.route("/flashcards/<int:card_id>")
def flashcard_detail(card_id):
    """Show a single flashcard with Hanzi Writer animation."""
    from_story = request.args.get("from_story", type=int)
    from_slice = request.args.get("slice", type=int)
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, chinese, english, description FROM flashcards WHERE id = %s", (card_id,))
            card = cur.fetchone()
            if card is None:
                return "Flashcard not found", 404
            story_title = None
            if from_story:
                cur.execute("SELECT title FROM stories WHERE id = %s", (from_story,))
                row = cur.fetchone()
                if row:
                    story_title = row[0]
    description_html = markdown.markdown(card[3]) if card[3] else None
    return render_template("flashcard_detail.html", card=card, from_story=from_story, from_slice=from_slice, story_title=story_title, description_html=description_html)


@app.route("/flashcards/add", methods=["GET", "POST"])
def flashcards_add():
    """Add a new flashcard."""
    preselect_slice_id = request.args.get("slice_id", type=int)
    preselect_story_id = request.args.get("story_id", type=int)

    with get_db() as conn:
        with conn.cursor() as cur:
            # Get all slices grouped by story for the form
            cur.execute("""
                SELECT ss.id, s.id as story_id, s.title, ss.slice_order
                FROM story_slices ss
                JOIN stories s ON ss.story_id = s.id
                ORDER BY s.created_at DESC, ss.slice_order
            """)
            slices = cur.fetchall()

    if request.method == "POST":
        chinese = request.form.get("chinese", "").strip()
        english = request.form.get("english", "").strip()
        description = request.form.get("description", "").strip()
        slice_ids = request.form.getlist("slices")
        from_story = request.form.get("from_story", type=int)
        if chinese and english:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO flashcards (chinese, english, description) VALUES (%s, %s, %s) RETURNING id",
                        (chinese, english, description or None)
                    )
                    card_id = cur.fetchone()[0]
                    for slice_id in slice_ids:
                        cur.execute(
                            "INSERT INTO flashcard_slices (flashcard_id, slice_id) VALUES (%s, %s)",
                            (card_id, int(slice_id))
                        )
                conn.commit()
            if from_story:
                return redirect(url_for("story", story_id=from_story))
            return redirect(url_for("flashcards"))
    linked_slice_ids = [preselect_slice_id] if preselect_slice_id else []
    return render_template("flashcards_form.html", card=None, slices=slices, linked_slice_ids=linked_slice_ids, from_story=preselect_story_id)


@app.route("/flashcards/<int:card_id>/edit", methods=["GET", "POST"])
def flashcards_edit(card_id):
    """Edit an existing flashcard."""
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, chinese, english, description FROM flashcards WHERE id = %s", (card_id,))
            card = cur.fetchone()
            if card is None:
                return "Flashcard not found", 404
            # Get all slices grouped by story
            cur.execute("""
                SELECT ss.id, s.id as story_id, s.title, ss.slice_order
                FROM story_slices ss
                JOIN stories s ON ss.story_id = s.id
                ORDER BY s.created_at DESC, ss.slice_order
            """)
            slices = cur.fetchall()
            cur.execute("SELECT slice_id FROM flashcard_slices WHERE flashcard_id = %s", (card_id,))
            linked_slice_ids = [row[0] for row in cur.fetchall()]

    if request.method == "POST":
        chinese = request.form.get("chinese", "").strip()
        english = request.form.get("english", "").strip()
        description = request.form.get("description", "").strip()
        slice_ids = request.form.getlist("slices")
        if chinese and english:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE flashcards SET chinese = %s, english = %s, description = %s WHERE id = %s",
                        (chinese, english, description or None, card_id)
                    )
                    cur.execute("DELETE FROM flashcard_slices WHERE flashcard_id = %s", (card_id,))
                    for slice_id in slice_ids:
                        cur.execute(
                            "INSERT INTO flashcard_slices (flashcard_id, slice_id) VALUES (%s, %s)",
                            (card_id, int(slice_id))
                        )
                conn.commit()
            return redirect(url_for("flashcard_detail", card_id=card_id))
    return render_template("flashcards_form.html", card=card, slices=slices, linked_slice_ids=linked_slice_ids, from_story=None)


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


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8080, debug=True)
