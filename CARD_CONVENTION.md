# Card HTML Convention

This document defines the contract for generating card HTML snippets. Claude Code MUST follow this convention when generating new cards for the sociology learning PWA.

**Related Documentation:**
- [CARD-CREATION-GUIDE.md](docs/CARD-CREATION-GUIDE.md) - Workflow and methodology
- [TASK-PAGES-ARCHITECTURE.md](docs/TASK-PAGES-ARCHITECTURE.md) - Task pages system

## Overview

Each card in the database contains a self-contained HTML snippet that:
1. Renders its own UI using Tailwind CSS
2. Manages its own interactivity using Alpine.js
3. Submits responses through a standardized mechanism

## Database Schema

### Cards Table

```sql
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    card_type VARCHAR(50) DEFAULT 'simple',     -- 'simple' | 'task_reference'
    card_html TEXT NOT NULL,
    response_schema JSONB,
    semantic_description TEXT,
    course_task_ref VARCHAR(255),
    course_id INTEGER REFERENCES courses(id),
    visibility VARCHAR(20) DEFAULT 'public',
    status VARCHAR(20) DEFAULT 'active',

    -- Tags for filtering (e.g., week blocks)
    tags TEXT[],                                -- e.g., ['Week 1-2'], ['Week 3-4']

    -- Task page reference (for task_reference cards)
    task_page_id VARCHAR(64) REFERENCES task_pages(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for efficient tag filtering
CREATE INDEX idx_cards_tags ON cards USING GIN(tags);
```

### Tags Convention

Tags are used to organize cards into content blocks for filtering:

| Tag | Content Block |
|-----|---------------|
| `Week 1-2` | First 2-week block (initial content) |
| `Week 3-4` | Second block |
| `Week 5-6` | Third block |
| `Week 7-8` | Fourth block |
| etc. | Continues as needed |

**Important:** When creating new cards, always include the appropriate `tags` array.

## Required Structure

Every card HTML snippet MUST wrap its content in a div with the `x-data="cardResponse()"` directive:

```html
<div x-data="cardResponse()" class="card-content">
    <!-- Card content here -->

    <!-- Submit button MUST use @click="submitResponse(responseData)" -->
    <button @click="submitResponse({ /* response object */ })"
            :disabled="submitting"
            class="...">
        <span x-show="!submitting">Submit</span>
        <span x-show="submitting">Sending...</span>
    </button>
</div>
```

## The cardResponse() Component

The app provides a global `cardResponse()` Alpine component with:

### State
- `submitting` (boolean): True while the response is being sent
- `submitted` (boolean): True after successful submission
- `error` (string|null): Error message if submission failed

### Methods
- `submitResponse(data)`: Submits the response to `POST /api/response`
  - `data`: A JavaScript object matching the card's `response_schema`
  - On success: Sets `submitted = true`, triggers card transition
  - On failure: Sets `error` with message

## Response Schema

Each card row has a `response_schema` (JSONB) that documents the expected shape of `response_content`. Claude Code generates both the schema and the card HTML that produces data matching it.

### Example Schema

```json
{
    "type": "object",
    "properties": {
        "answer": { "type": "string" },
        "confidence": { "type": "integer", "minimum": 1, "maximum": 5 }
    },
    "required": ["answer"]
}
```

### Example Matching Card HTML

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '', confidence: 3 }">
        <h2 class="text-lg font-semibold mb-3">Was ist Sozialisation?</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border rounded-lg mb-4"
                  rows="4"
                  placeholder="Deine Antwort..."></textarea>

        <label class="block mb-2 text-sm">Wie sicher bist du? (1-5)</label>
        <input type="range" x-model="confidence" min="1" max="5"
               class="w-full mb-4">
        <p class="text-center text-sm mb-4" x-text="confidence + '/5'"></p>

        <button @click="submitResponse({ answer, confidence: parseInt(confidence) })"
                :disabled="submitting || answer.trim() === ''"
                class="w-full py-3 bg-indigo-600 text-white rounded-lg disabled:opacity-50">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>
```

## Card Types Reference

### 1. Free Text Response

For open-ended questions requiring written answers.

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Lernziel: Begriff definieren</p>
        <h2 class="text-lg font-semibold mb-4">[Question in German]</h2>

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
    </div>
</div>
```

Response schema:
```json
{ "type": "object", "properties": { "answer": { "type": "string" } }, "required": ["answer"] }
```

### 2. Multiple Choice

For testing factual recall or concept recognition.

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">[Question]</h2>

        <div class="space-y-2">
            <template x-for="(option, index) in ['Option A', 'Option B', 'Option C', 'Option D']" :key="index">
                <button @click="selected = index"
                        :class="selected === index ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                        class="w-full p-3 text-left border rounded-lg transition-colors">
                    <span x-text="option"></span>
                </button>
            </template>
        </div>

        <button @click="submitResponse({ selected_index: selected })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Bestätigen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>
```

Response schema:
```json
{ "type": "object", "properties": { "selected_index": { "type": "integer" } }, "required": ["selected_index"] }
```

### 3. Self-Assessment (Reveal & Rate)

For flashcard-style memorization with self-rating.

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">[Term to define]</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800">[Definition/Answer]</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gut</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Weiter</span>
                <span x-show="submitting">Wird gesendet...</span>
            </button>
        </div>
    </div>
</div>
```

Response schema:
```json
{ "type": "object", "properties": { "self_rating": { "type": "integer", "minimum": 1, "maximum": 3 } }, "required": ["self_rating"] }
```

### 4. Fill in the Blank

For testing specific terminology.

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Ergänze den fehlenden Begriff</p>

        <p class="text-lg mb-4">
            Die _______ beschreibt den Prozess, durch den Individuen die Normen und Werte einer Gesellschaft erlernen.
        </p>

        <input type="text" x-model="answer"
               class="w-full p-3 border border-gray-300 rounded-lg text-center text-lg"
               placeholder="Begriff eingeben">

        <button @click="submitResponse({ blank_answer: answer.trim() })"
                :disabled="submitting || answer.trim() === ''"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Prüfen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>
```

Response schema:
```json
{ "type": "object", "properties": { "blank_answer": { "type": "string" } }, "required": ["blank_answer"] }
```

### 5. Ordering/Ranking

For testing understanding of sequences or priorities.

```html
<div x-data="cardResponse()" class="p-4">
    <div x-data="{
        items: ['Item A', 'Item B', 'Item C', 'Item D'],
        dragIndex: null,
        moveUp(i) { if (i > 0) { [this.items[i-1], this.items[i]] = [this.items[i], this.items[i-1]] } },
        moveDown(i) { if (i < this.items.length - 1) { [this.items[i], this.items[i+1]] = [this.items[i+1], this.items[i]] } }
    }">
        <p class="text-gray-600 text-sm mb-2">Bringe diese Elemente in die richtige Reihenfolge</p>
        <h2 class="text-lg font-semibold mb-4">[Instruction]</h2>

        <div class="space-y-2">
            <template x-for="(item, index) in items" :key="item">
                <div class="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                    <span class="text-gray-400 font-mono" x-text="index + 1"></span>
                    <span class="flex-1" x-text="item"></span>
                    <button @click="moveUp(index)" class="p-1 text-gray-500">↑</button>
                    <button @click="moveDown(index)" class="p-1 text-gray-500">↓</button>
                </div>
            </template>
        </div>

        <button @click="submitResponse({ order: items })"
                :disabled="submitting"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Reihenfolge bestätigen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>
```

Response schema:
```json
{ "type": "object", "properties": { "order": { "type": "array", "items": { "type": "string" } } }, "required": ["order"] }
```

### 6. Task Reference Card

For linking to a task page (interactive exercises rendered in iframe). These cards display task status and provide navigation to the full task page.

```html
<div x-data="cardResponse()" class="p-4">
    <div class="flex items-start gap-3">
        <div class="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/>
            </svg>
        </div>
        <div class="flex-1">
            <h3 class="font-semibold text-gray-800">[Task Title]</h3>
            <p class="text-sm text-gray-600 mt-1">[Task Description]</p>
            <div class="flex items-center gap-2 mt-2">
                <span class="text-xs px-2 py-1 bg-amber-100 text-amber-700 rounded">~30 Min</span>
                <span class="text-xs text-gray-500">Übung</span>
            </div>
        </div>
    </div>

    <button @click="submitResponse({ action: 'open_task' })"
            class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium">
        Aufgabe öffnen
    </button>
</div>
```

**Note:** Task reference cards require:
- `card_type = 'task_reference'`
- `task_page_id` set to the task page ID
- The PWA handles navigation to the task page when the response is submitted

Response schema:
```json
{ "type": "object", "properties": { "action": { "type": "string" } }, "required": ["action"] }
```

## Styling Guidelines

1. **Use Tailwind utility classes only** - no custom CSS
2. **Mobile-first**: Design for 375px viewport width
3. **Consistent spacing**: Use `p-4` for card padding, `mb-4` between sections
4. **Color palette**:
   - Primary: `indigo-600` (buttons, focus states)
   - Text: `gray-800` (primary), `gray-600` (secondary)
   - Backgrounds: `gray-50`, `gray-100` (subtle), white (cards)
   - Success: `green-600`
   - Warning: `yellow-600`
   - Error: `red-600`
5. **Typography**:
   - Questions: `text-lg font-semibold`
   - Body text: `text-base`
   - Labels: `text-sm text-gray-600`
6. **Buttons**: Full width (`w-full`), rounded (`rounded-lg`), with padding (`py-3`)
7. **Inputs**: Full width, border, rounded, with focus ring

## Important Rules

1. **Never hardcode card_id** - the app injects it automatically
2. **Always use the `submitResponse()` function** - never call fetch directly
3. **Handle loading state** with `:disabled="submitting"` and visual feedback
4. **Validate before submit** - disable button if required fields are empty
5. **Use `x-cloak`** on elements that should be hidden initially (prevents flash)
6. **German language** - all user-facing text should be in German
7. **Semantic descriptions** - ensure `semantic_description` in the cards table clearly explains the learning goal

## Testing Cards Locally

To test a card before inserting into the database:

1. Place the HTML in the test harness at `/test-card`
2. The harness provides a mock `cardResponse()` that logs to console
3. Verify all interactions work before generating the INSERT statement

## Database INSERT Templates

### Standard Learning Card

```sql
INSERT INTO cards (
    card_type, semantic_description, course_task_ref, course_id,
    status, card_html, response_schema, tags
)
VALUES (
    'simple',
    'Learning goal description for Claude Code reasoning',
    'Optional: Übung A - Task 3',
    (SELECT id FROM courses WHERE slug = 'sociology'),
    'active',
    E'<div x-data="cardResponse()" class="p-4">...</div>',
    '{"type": "object", "properties": {...}, "required": [...]}'::jsonb,
    ARRAY['Week 1-2']  -- Tag for content filtering
);
```

### Task Reference Card (links to task page)

```sql
-- First, create the task page
INSERT INTO task_pages (id, title, description, page_html, course_id, topics, tags, estimated_duration_minutes, difficulty)
VALUES (
    'ubung-b-article-analysis',
    'Übung B: Forschungsartikel analysieren',
    'Recherchiere und analysiere einen wissenschaftlichen Artikel.',
    '<!DOCTYPE html>...',  -- Full HTML document
    (SELECT id FROM courses WHERE slug = 'sociology'),
    ARRAY['forschungsartikel', 'literaturrecherche'],
    ARRAY['Week 3-4'],
    45,
    'intermediate'
);

-- Then, create a task_reference card pointing to it
INSERT INTO cards (
    card_type, task_page_id, course_id, semantic_description,
    visibility, card_html, response_schema, tags
)
VALUES (
    'task_reference',
    'ubung-b-article-analysis',
    (SELECT id FROM courses WHERE slug = 'sociology'),
    'Aufgabe: Übung B - Forschungsartikel',
    'public',
    '',  -- Card HTML can be empty; PWA generates display from task page metadata
    '{}',
    ARRAY['Week 3-4']
);
```

### Notes

- Use `E'...'` syntax for card_html to handle escaped characters
- Always include `tags` array for content filtering
- Task reference cards can have empty `card_html`; the PWA displays task page info
- Use consistent tag naming: `Week 1-2`, `Week 3-4`, etc.

---

## Task Pages

For complex, interactive learning experiences, use task pages instead of inline cards. Task pages are rendered in an iframe and have their own API for saving drafts and submitting responses.

See [TASK-PAGES-ARCHITECTURE.md](docs/TASK-PAGES-ARCHITECTURE.md) for full documentation.

### Task Page HTML Template

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Title</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
    window.COMMUTE_CONFIG = {
        deviceToken: '{{device_token}}',
        taskPageId: '{{task_page_id}}',
        apiBase: '{{api_base}}'
    };
    </script>
    <script src="/static/js/task-api.js"></script>
</head>
<body class="bg-gray-50">
    <div class="max-w-2xl mx-auto p-4 pb-20">
        <!-- Task content here -->
    </div>

    <script>
    // Use TaskAPI for interactions:
    // - TaskAPI.saveDraft(notes) - Save draft/notes
    // - TaskAPI.submitResponse(data) - Submit response data
    // - TaskAPI.complete() - Mark task as completed
    // - TaskAPI.getStatus() - Get current status (includes saved notes)
    </script>
</body>
</html>
```

### TaskAPI Methods

| Method | Description |
|--------|-------------|
| `TaskAPI.getStatus()` | Get current status and saved notes |
| `TaskAPI.saveDraft(notes)` | Save draft notes (string) |
| `TaskAPI.submitResponse(data)` | Submit response data (object) |
| `TaskAPI.complete()` | Mark task as completed |
| `TaskAPI.setStatus(status)` | Set status: 'not_started', 'in_progress', 'completed' |