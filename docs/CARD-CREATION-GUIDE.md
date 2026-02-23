# Card Creation Guide

This document describes the complete workflow for creating learning cards for the sociology PWA. It complements `CARD_CONVENTION.md` (technical HTML patterns) with methodology, workflow, and best practices.

## Table of Contents

1. [Pre-Creation Workflow](#pre-creation-workflow)
2. [Card Types & Use Cases](#card-types--use-cases)
3. [Content Sources](#content-sources)
4. [Creating Different Card Categories](#creating-different-card-categories)
5. [Database Operations](#database-operations)
6. [Best Practices & Lessons Learned](#best-practices--lessons-learned)

---

## Pre-Creation Workflow

**CRITICAL: Always follow this workflow before generating new cards.**

### Step 1: Check Existing Cards

Before creating ANY new cards, query the database to see what already exists:

```bash
fly ssh console -C "psql \$DATABASE_URL -c \"SELECT id, semantic_description, course_task_ref FROM cards ORDER BY id;\""
```

This prevents:
- Duplicate cards on the same topic
- Overlapping content that confuses the learner
- Wasted effort creating cards that already exist

### Step 2: Check User Responses (if applicable)

If creating evaluation/reflection cards based on user performance:

```bash
fly ssh console -C "psql \$DATABASE_URL -c \"SELECT c.semantic_description, r.response_content, r.created_at FROM responses r JOIN cards c ON r.card_id = c.id ORDER BY r.created_at DESC LIMIT 20;\""
```

This allows you to:
- See which cards the user has already answered
- Evaluate their understanding based on responses
- Create targeted follow-up cards addressing weaknesses

### Step 3: Review Course Materials

Check which topics are covered in the current course materials:
- `/materials/sociology/` - Course PDFs and transcripts
- `/exercises/` - Exercise files (Übungen)
- `/study_schedule/` - Course structure and timeline
- `/knowledge-base/` - Deep-dive research notes

### Step 4: Identify Gaps

Based on Steps 1-3, identify:
- Topics covered in materials but not yet in cards
- Areas where user responses showed misunderstanding
- Course tasks that need practice cards

---

## Card Types & Use Cases

### 1. Self-Assessment (Reveal & Rate)

**Use when:** Testing recall of definitions, concepts, or facts where the answer is clear-cut.

**Best for:**
- Vocabulary/terminology
- Key definitions
- Historical facts
- Formula recall

**Response data:** `{ self_rating: 1|2|3 }` (Gar nicht / Teilweise / Gut)

### 2. Multiple Choice

**Use when:** Testing distinction between similar concepts, or factual recall with verifiable answers.

**Best for:**
- Policy vs Polity vs Politics distinctions
- Identifying correct definitions
- Literature type identification (Monographie vs Sammelband)
- Testing understanding of multi-level governance

**Response data:** `{ selected_index: number, correct_answer: number }`

### 3. Fill in the Blank

**Use when:** Testing specific terminology in context.

**Best for:**
- German technical terms (Vollzug, Sozialisation, etc.)
- Key phrases from course materials
- Completing definitions

**Response data:** `{ blank_answer: string, correct_answer: string }`

### 4. Ordering/Ranking

**Use when:** Testing understanding of sequences, hierarchies, or priorities.

**Best for:**
- Abfallpyramide (waste hierarchy)
- Multi-level governance flows
- Process steps
- Priority rankings

**Response data:** `{ order: string[] }`

### 5. Free Text Response

**Use when:** Encouraging deeper thinking and articulation of understanding.

**Best for:**
- Open-ended explanations
- Comparison questions
- Opinion/analysis questions
- Applying concepts to scenarios

**Response data:** `{ answer: string }`

### 6. Action/Research Task

**Use when:** Guiding the user to engage with external resources.

**Best for:**
- Links to Moodle course pages
- PDF reading assignments
- Research tasks from Übungen
- Forum participation prompts

**Response data:** `{ completed: boolean }` or `{ link_clicked: boolean }`

### 7. Reflection/Evaluation Card

**Use when:** Providing feedback on previous responses.

**Structure:**
- Shows the user's previous answer
- Provides evaluation/correction
- Links to relevant textbook sources
- Suggests further reading

**Best for:**
- Wrong answers that need correction
- Partial answers that need expansion
- Connecting responses to source materials

---

## Content Sources

### Available Materials

| Source | Location | Use For |
|--------|----------|---------|
| PDF Manifest | `/materials/manifest.json` | Direct links to Firebase-hosted PDFs |
| Transcripts | `/materials/sociology/transcripts/` | Video content summaries |
| Exercises | `/exercises/UBUNG_A.md`, etc. | Task references |
| Study Schedule | `/study_schedule/` | Course structure, deadlines |
| Knowledge Base | `/knowledge-base/` | Deep research notes |

### PDF Link Format

When linking to specific PDF pages:

```
https://firebasestorage.googleapis.com/v0/b/YOUR-BUCKET/o/ENCODED-PATH?alt=media#page=X
```

Example:
```html
<a href="https://firebasestorage.googleapis.com/...&alt=media#page=45"
   target="_blank"
   class="text-indigo-600 underline">
   Kapitel 3: Politikfeldanalyse (S. 45)
</a>
```

### Course Task References

Use the `course_task_ref` field to link cards to specific course tasks:

- `"Übung A - Task 3"` - Policy/Polity/Politics identification
- `"Übung A - Task 4"` - Video analysis (Circular Cities)
- `"Übung A - Task 5"` - Research methods
- `"Kurs 25501 - Einheit 1"` - Course unit reference

---

## Creating Different Card Categories

### Category 1: Concept Cards

Cards that test understanding of course concepts.

**Workflow:**
1. Identify key concepts from study materials
2. Create mix of self-assessment and multiple choice
3. Use German terminology with explanations
4. Link to source materials where helpful

### Category 2: Evaluation/Reflection Cards

Cards that respond to user's previous answers.

**Workflow:**
1. Query user responses from database
2. Analyze correctness and completeness
3. Create cards that:
   - Quote their answer
   - Provide correction/evaluation
   - Link to relevant sources
   - Suggest how to improve

**Example structure:**
```html
<div class="p-4 bg-amber-50 border-l-4 border-amber-500 rounded mb-4">
    <p class="text-sm text-amber-800 font-medium">Deine Antwort:</p>
    <p class="text-amber-900 italic">"[User's actual response]"</p>
</div>

<div class="p-4 bg-green-50 border-l-4 border-green-500 rounded mb-4">
    <p class="text-sm text-green-800 font-medium">Bewertung:</p>
    <p class="text-green-900">[Evaluation text]</p>
</div>

<a href="[PDF link]" class="text-indigo-600 underline">
    Lies mehr dazu in Kapitel X
</a>
```

### Category 3: Course Orientation Cards

Cards about course structure, duties, and logistics.

**Topics to cover:**
- Course timeline and phases
- Submission requirements
- Forum participation expectations
- Exam format
- Study group information
- Administrative deadlines

### Category 4: Research Task Cards

Cards that guide engagement with course tasks.

**Structure:**
- Describe the research task
- Provide direct link (Moodle, library, etc.)
- Give clear instructions
- Track completion

---

## Database Operations

### Inserting Cards via Fly.io

**Method 1: Python Script**

Create a Python script (e.g., `/tmp/insert_cards.py`):

```python
import os
import json
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL")

cards = [
    {
        "semantic_description": "Description of learning goal",
        "course_task_ref": "Übung A - Task X",
        "card_html": '''<div x-data="cardResponse()" class="p-4">
            <!-- Card HTML here -->
        </div>''',
        "response_schema": {
            "type": "object",
            "properties": {...},
            "required": [...]
        }
    },
    # More cards...
]

with psycopg.connect(DATABASE_URL) as conn:
    with conn.cursor() as cur:
        for card in cards:
            cur.execute(
                """INSERT INTO cards (semantic_description, course_task_ref, status, card_html, response_schema)
                   VALUES (%s, %s, 'active', %s, %s)""",
                (card["semantic_description"], card["course_task_ref"],
                 card["card_html"], json.dumps(card["response_schema"]))
            )
            print(f"Inserted: {card['semantic_description'][:50]}...")
    conn.commit()
    print(f"\nSuccessfully inserted {len(cards)} cards!")
```

**Upload and run (one-liner to avoid timeout issues):**
```bash
# Wake app, upload, and run in quick succession
curl -s https://sociology-learning-pwa.fly.dev/health && \
fly ssh sftp shell <<EOF
put /tmp/insert_cards.py /tmp/insert_cards.py
EOF
fly ssh console -C "python /tmp/insert_cards.py"
```

### Checking Card Status

Use Python instead of psql (psql is not installed in the container):

```bash
# List all cards
fly ssh console -C "python -c \"
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT id, semantic_description, course_task_ref FROM cards ORDER BY id')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1][:60]}... | {row[2]}')
\""

# Check recent responses
fly ssh console -C "python -c \"
import os, psycopg
conn = psycopg.connect(os.environ['DATABASE_URL'])
cur = conn.cursor()
cur.execute('SELECT card_id, response_content FROM responses ORDER BY responded_at DESC LIMIT 10')
for row in cur.fetchall():
    print(f'Card {row[0]}: {str(row[1])[:80]}')
\""
```

### Fly.io Troubleshooting

**Problem: App scales to zero quickly**

Fly.io auto-scales the app to zero VMs when idle. This causes:
- `fly ssh console` fails with "app has no started VMs"
- `fly ssh sftp` fails similarly
- Files in `/tmp` are lost when VM restarts

**Solution: Wake → Upload → Run in quick succession**

```bash
# Step 1: Wake up the app
curl -s https://sociology-learning-pwa.fly.dev/health

# Step 2: Immediately upload (while VM is still running)
fly ssh sftp shell <<EOF
put /tmp/insert_cards.py /tmp/insert_cards.py
EOF

# Step 3: Immediately run (before VM scales down again)
fly ssh console -C "python /tmp/insert_cards.py"
```

**If you get "tunnel unavailable" or timeout errors:**
- Wait a few seconds and retry
- The Fly.io API can be slow sometimes
- Try the wake-up curl again before retrying

**If you get "No such file" error:**
- The VM restarted and `/tmp` was wiped
- Re-upload the script and run immediately

**One-liner for reliability:**
```bash
curl -s https://sociology-learning-pwa.fly.dev/health && \
fly ssh sftp shell <<< "put /tmp/insert_cards.py /tmp/insert_cards.py" && \
fly ssh console -C "python /tmp/insert_cards.py"
```

---

## Best Practices & Lessons Learned

### DO:

1. **Always check existing cards first** - Prevents duplicates and ensures coverage gaps are real
2. **Check user responses before creating evaluation cards** - Base feedback on actual data
3. **Use consistent card types for similar content** - Creates predictable learning patterns
4. **Include source links** - Helps users go deeper on topics
5. **Use German for all user-facing text** - Matches course language
6. **Test card HTML before bulk insertion** - Prevents broken cards in production
7. **Use meaningful `semantic_description`** - Helps with future card management
8. **Include `course_task_ref`** - Links cards to course structure

### DON'T:

1. **Create cards without checking the database** - You WILL create duplicates
2. **Assume what topics need coverage** - Check materials and existing cards
3. **Make evaluation cards without checking actual responses** - Generic feedback is unhelpful
4. **Hardcode card IDs** - The app injects them automatically
5. **Use external CSS/JS** - Everything must use Tailwind and Alpine.js
6. **Create too many similar cards at once** - Variety improves engagement

### Common Mistakes to Avoid:

| Mistake | Why It Happens | How to Avoid |
|---------|---------------|--------------|
| Duplicate cards | Not checking existing cards | Always query DB first |
| Generic evaluation | Not reading actual responses | Query responses before creating |
| Broken HTML | Missing Alpine directives | Test in browser first |
| Wrong language | Copy-pasting from English sources | Write fresh in German |
| Missing submit button | Incomplete card template | Use full patterns from CARD_CONVENTION.md |

---

## Card Quality Checklist

Before inserting any card, verify:

- [ ] `semantic_description` clearly explains the learning goal
- [ ] `course_task_ref` links to correct course element (if applicable)
- [ ] Card HTML starts with `<div x-data="cardResponse()">`
- [ ] Submit button uses `submitResponse({...})`
- [ ] All user-facing text is in German
- [ ] Response schema matches data being submitted
- [ ] No duplicate of existing card
- [ ] Source links use correct Firebase Storage URLs with `#page=X`
- [ ] Card renders correctly on mobile viewport (375px)

---

## File References

- **Technical HTML patterns:** `/CARD_CONVENTION.md`
- **This workflow guide:** `/docs/CARD-CREATION-GUIDE.md`
- **Authentication concept:** `/docs/AUTHENTICATION-CONCEPT.md`
- **PDF manifest:** `/materials/manifest.json`
- **Exercise files:** `/exercises/`
- **Study schedule:** `/study_schedule/`