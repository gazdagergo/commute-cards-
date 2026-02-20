# Card HTML Convention

This document defines the contract for generating card HTML snippets. Claude Code MUST follow this convention when generating new cards for the sociology learning PWA.

## Overview

Each card in the database contains a self-contained HTML snippet that:
1. Renders its own UI using Tailwind CSS
2. Manages its own interactivity using Alpine.js
3. Submits responses through a standardized mechanism

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

## Database INSERT Template

When generating a new card:

```sql
INSERT INTO cards (semantic_description, course_task_ref, status, card_html, response_schema)
VALUES (
    'Learning goal description for Claude Code reasoning',
    'Optional: course-task-id-123',
    'active',
    E'<div x-data="cardResponse()" class="p-4">...</div>',
    '{"type": "object", "properties": {...}, "required": [...]}'::jsonb
);
```

Note: Use `E'...'` syntax for the card_html to handle any escaped characters properly.