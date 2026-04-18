# Task Pages Architecture

## Overview

A refined architecture that separates **scheduling/organization** from **learning content**:

- **Cards** = lightweight scheduling units (filtering, reminders, topic pointers)
- **Task Pages** = standalone, LLM-generated HTML/CSS/JS pages for rich learning experiences
- **PWA** = thin shell that hosts both, with task pages rendered in isolated iframes

This keeps the app layer thin while enabling arbitrarily complex, interactive learning content.

---

## Design Principles

### 1. Separation of Concerns
- Cards handle: scheduling, filtering, topic organization, reminders
- Task pages handle: content, interaction, response submission, evaluation
- PWA handles: navigation, offline caching, device identity

### 2. Task Pages are First-Class Entities
- Own lifecycle: `draft` → `in_progress` → `completed`
- Own response handling and evaluation storage
- Self-contained HTML/CSS/JS — no framework dependencies
- Multiple cards can reference the same task page

### 3. Isolation via iframe
- Task page JS/CSS cannot break the PWA
- Clean security boundary
- Task page communicates with server via standard REST API
- PWA injects device token at render time

### 4. Offline-First Preserved
- Service worker caches task page HTML
- Task pages work offline (read-only mode)
- Status updates queue locally when offline

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                            PWA Shell                                │
│                         (Alpine.js app)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │   Card List      │  │   Simple Card    │  │   Task Page      │   │
│  │     View         │  │     View         │  │     View         │   │
│  │                  │  │                  │  │                  │   │
│  │  • Scheduling    │  │  • Quick cards   │  │  ┌────────────┐  │   │
│  │  • Filtering     │  │  • In-app Alpine │  │  │  <iframe>  │  │   │
│  │  • Task status   │  │  • Flashcards    │  │  │            │  │   │
│  │    badges        │  │  • Simple MCQ    │  │  │  LLM-gen   │  │   │
│  │  • Navigation    │  │                  │  │  │  HTML/CSS  │  │   │
│  │                  │  │                  │  │  │  /JS       │  │   │
│  │                  │  │                  │  │  │            │  │   │
│  └──────────────────┘  └──────────────────┘  │  └─────┬──────┘  │   │
│                                              │        │         │   │
│                                              │        │ fetch() │   │
│                                              │        ▼         │   │
│                                              │  ┌────────────┐  │   │
│                                              │  │ Server API │  │   │
│                                              │  └────────────┘  │   │
│                                              └──────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            Server                                   │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │
│  │   Cards     │  │ Task Pages  │  │  Statuses   │  │ Responses │   │
│  │  (schedule) │──│  (content)  │──│(per device) │──│(per page) │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Server (PostgreSQL)

```sql
-- Task Pages: standalone learning content
CREATE TABLE task_pages (
    id VARCHAR(64) PRIMARY KEY,           -- e.g., "sociology-kreislauf-01"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT,
    page_html TEXT NOT NULL,              -- LLM-generated HTML/CSS/JS

    -- Organization
    course_id VARCHAR(64) REFERENCES courses(id),
    topics TEXT[],                        -- e.g., ['kreislaufwirtschaft', 'nachhaltigkeit']

    -- Metadata
    estimated_duration_minutes INTEGER,
    difficulty VARCHAR(20),               -- 'beginner' | 'intermediate' | 'advanced'
    generation_batch VARCHAR(64)          -- Track which LLM generation created this
);

-- Task Page Status: per-device progress
CREATE TABLE task_page_statuses (
    id SERIAL PRIMARY KEY,
    task_page_id VARCHAR(64) REFERENCES task_pages(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,

    status VARCHAR(20) DEFAULT 'not_started',  -- 'not_started' | 'draft' | 'in_progress' | 'completed'
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Local notes (optional server backup)
    notes TEXT,

    UNIQUE(task_page_id, device_token)
);

-- Task Page Responses: submissions for a task page
CREATE TABLE task_page_responses (
    id SERIAL PRIMARY KEY,
    task_page_id VARCHAR(64) REFERENCES task_pages(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,

    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_content JSONB NOT NULL,

    -- Evaluation
    evaluation JSONB,                     -- LLM-generated feedback
    evaluated_at TIMESTAMP
);

-- Cards: now primarily scheduling/reference
-- (existing table, with new optional column)
ALTER TABLE cards ADD COLUMN task_page_id VARCHAR(64) REFERENCES task_pages(id);

-- Indexes
CREATE INDEX idx_task_pages_course ON task_pages(course_id);
CREATE INDEX idx_task_page_statuses_device ON task_page_statuses(device_token);
CREATE INDEX idx_task_page_statuses_lookup ON task_page_statuses(task_page_id, device_token);
CREATE INDEX idx_task_page_responses_lookup ON task_page_responses(task_page_id, device_token);
```

### PWA (IndexedDB additions)

```javascript
// New stores for task pages
const additionalStores = {
    // Cached task pages
    task_pages: {
        keyPath: 'id',
        indexes: ['course_id', 'updated_at']
        // { id, title, page_html, topics, ... }
    },

    // Local task page status (synced with server)
    task_page_statuses: {
        keyPath: 'task_page_id',
        // { task_page_id, status, started_at, completed_at, updated_at }
    },

    // Pending status updates (offline queue)
    pending_task_updates: {
        keyPath: 'id',
        autoIncrement: true
        // { task_page_id, status, timestamp }
    }
};
```

---

## API Endpoints

### Task Page Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/task-pages` | List task pages (with filters) |
| GET | `/api/task-pages/:id` | Get task page with current status |
| GET | `/api/task-pages/:id/html` | Get raw HTML for iframe |

### Task Page Status Endpoints (authenticated via device token)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/task-pages/:id/status` | Get status for device |
| POST | `/api/task-pages/:id/status` | Update status |
| POST | `/api/task-pages/:id/response` | Submit response |
| GET | `/api/task-pages/:id/evaluation` | Get evaluation (if available) |
| GET | `/api/task-pages/:id/responses` | Get all responses for device |

### Batch Status Endpoint (for PWA sync)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/task-pages/statuses` | Get statuses for multiple pages |

### Request/Response Examples

```javascript
// Get task page with status
GET /api/task-pages/sociology-kreislauf-01
Headers: { "X-Device-Token": "abc123..." }

// Response
{
    "id": "sociology-kreislauf-01",
    "title": "Kreislaufwirtschaft verstehen",
    "description": "Interaktive Übung zu...",
    "course_id": "sociology",
    "topics": ["kreislaufwirtschaft", "nachhaltigkeit"],
    "estimated_duration_minutes": 15,
    "status": {
        "status": "in_progress",
        "started_at": "2024-03-15T10:00:00Z",
        "updated_at": "2024-03-15T10:30:00Z"
    },
    "has_evaluation": false
}

// Update status
POST /api/task-pages/sociology-kreislauf-01/status
Headers: { "X-Device-Token": "abc123..." }
Body: { "status": "completed" }

// Response
{
    "success": true,
    "status": "completed",
    "completed_at": "2024-03-15T11:00:00Z"
}

// Submit response
POST /api/task-pages/sociology-kreislauf-01/response
Headers: { "X-Device-Token": "abc123..." }
Body: {
    "response_content": {
        "answers": [...],
        "reflection": "..."
    }
}

// Response
{
    "success": true,
    "response_id": 42,
    "submitted_at": "2024-03-15T11:00:00Z"
}
```

---

## Task Page Structure

### HTML Template

Task pages are self-contained HTML documents rendered in an iframe:

```html
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Page-specific styles */
    </style>
</head>
<body class="bg-gray-50 p-4">
    <!-- Task content -->
    <div class="max-w-lg mx-auto">
        <h1 class="text-xl font-bold mb-4">Kreislaufwirtschaft</h1>

        <!-- Interactive content here -->
        <div id="task-content">
            ...
        </div>

        <!-- Status/submission controls -->
        <div id="task-controls" class="mt-6 border-t pt-4">
            <div class="flex gap-2">
                <button onclick="TaskAPI.setStatus('in_progress')"
                        class="px-4 py-2 bg-yellow-500 text-white rounded">
                    In Bearbeitung
                </button>
                <button onclick="TaskAPI.setStatus('completed')"
                        class="px-4 py-2 bg-green-500 text-white rounded">
                    Abgeschlossen
                </button>
            </div>
        </div>
    </div>

    <!-- Task API Bootstrap -->
    <script>
        window.COMMUTE_CONFIG = {
            deviceToken: "{{device_token}}",
            taskPageId: "{{task_page_id}}",
            apiBase: "{{api_base}}"
        };
    </script>
    <script src="/static/js/task-api.js"></script>
    <script>
        /* Page-specific JavaScript */
    </script>
</body>
</html>
```

### Task API Library (`/static/js/task-api.js`)

A small library included in every task page:

```javascript
const TaskAPI = {
    config: window.COMMUTE_CONFIG,

    async setStatus(status) {
        const response = await fetch(
            `${this.config.apiBase}/task-pages/${this.config.taskPageId}/status`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Device-Token': this.config.deviceToken
                },
                body: JSON.stringify({ status })
            }
        );
        return response.json();
    },

    async submitResponse(content) {
        const response = await fetch(
            `${this.config.apiBase}/task-pages/${this.config.taskPageId}/response`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Device-Token': this.config.deviceToken
                },
                body: JSON.stringify({ response_content: content })
            }
        );
        return response.json();
    },

    async getEvaluation() {
        const response = await fetch(
            `${this.config.apiBase}/task-pages/${this.config.taskPageId}/evaluation`,
            {
                headers: {
                    'X-Device-Token': this.config.deviceToken
                }
            }
        );
        return response.json();
    },

    async getStatus() {
        const response = await fetch(
            `${this.config.apiBase}/task-pages/${this.config.taskPageId}/status`,
            {
                headers: {
                    'X-Device-Token': this.config.deviceToken
                }
            }
        );
        return response.json();
    }
};

// Auto-initialize status display if element exists
document.addEventListener('DOMContentLoaded', async () => {
    const statusEl = document.getElementById('current-status');
    if (statusEl) {
        const data = await TaskAPI.getStatus();
        statusEl.textContent = data.status || 'not_started';
    }
});
```

---

## PWA Integration

### Rendering Task Pages

```javascript
// In app.js - Task page view component
Alpine.data('taskPageView', () => ({
    taskPageId: null,
    taskPage: null,
    loading: true,

    async loadTaskPage(id) {
        this.taskPageId = id;
        this.loading = true;

        // Fetch task page (from cache or server)
        this.taskPage = await db.getTaskPage(id);
        if (!this.taskPage) {
            this.taskPage = await api.fetchTaskPage(id);
            await db.cacheTaskPage(this.taskPage);
        }

        this.loading = false;
        this.renderInIframe();
    },

    renderInIframe() {
        const iframe = this.$refs.taskFrame;
        const deviceToken = await db.getDeviceToken();

        // Inject config into HTML
        let html = this.taskPage.page_html;
        html = html.replace('{{device_token}}', deviceToken);
        html = html.replace('{{task_page_id}}', this.taskPageId);
        html = html.replace('{{api_base}}', '/api');

        iframe.srcdoc = html;
    }
}));
```

### Template

```html
<!-- Task page view in index.html -->
<div x-data="taskPageView" x-show="currentView === 'task-page'">
    <div class="p-4 border-b flex items-center gap-2">
        <button @click="goBack()" class="text-blue-600">&larr; Zurück</button>
        <span x-text="taskPage?.title" class="font-medium"></span>
    </div>

    <div x-show="loading" class="p-8 text-center text-gray-500">
        Laden...
    </div>

    <iframe
        x-ref="taskFrame"
        x-show="!loading"
        class="w-full border-0"
        style="height: calc(100vh - 60px);"
        sandbox="allow-scripts allow-forms allow-same-origin"
    ></iframe>
</div>
```

### Card Integration

Cards can reference task pages and display status:

```javascript
// Card with task page reference
{
    "id": 101,
    "card_type": "task_reference",
    "task_page_id": "sociology-kreislauf-01",
    "card_html": "...",  // Simple card showing task status + link
    "semantic_description": "Reminder to continue Kreislaufwirtschaft exercise"
}

// When displaying such a card, fetch current status
async displayTaskCard(card) {
    const status = await api.getTaskPageStatus(card.task_page_id);
    // Render card with status badge
}
```

### Smart Card Generation

The system can generate contextual cards based on task page status:

| Task Status | Card Types Generated |
|-------------|---------------------|
| `not_started` | Introduction card, "Start this task" prompt |
| `in_progress` | "Continue your work" reminder |
| `completed` | Review cards, follow-up questions |
| `has_evaluation` | "View your feedback" card |

---

## Offline Behavior

### Task Pages
- Service worker caches task page HTML on first load
- Task pages render offline (read-only)
- Status updates queue in `pending_task_updates`
- Response submissions queue locally
- Sync on reconnect

### Status Sync

```javascript
// On app startup or reconnect
async syncTaskStatuses() {
    // Upload pending updates
    const pending = await db.getPendingTaskUpdates();
    for (const update of pending) {
        try {
            await api.updateTaskStatus(update.task_page_id, update.status);
            await db.removePendingUpdate(update.id);
        } catch (e) {
            if (!navigator.onLine) break;
        }
    }

    // Fetch latest statuses for cached task pages
    const cachedPages = await db.getAllTaskPages();
    const pageIds = cachedPages.map(p => p.id);
    const statuses = await api.batchGetStatuses(pageIds);

    for (const status of statuses) {
        await db.updateTaskPageStatus(status.task_page_id, status);
    }
}
```

---

## Card Types Summary

After this architecture, cards fall into these categories:

| Type | Location | Complexity | Use Case |
|------|----------|------------|----------|
| `simple` | In-app (Alpine) | Low | Flashcards, quick MCQ, self-assessment |
| `task_reference` | In-app (Alpine) | Low | Link to task page + status display |
| `reminder` | In-app (Alpine) | Low | "Continue X", "Review Y" prompts |
| `task_page` | iframe | Any | Full learning exercises, complex interactions |

---

## Migration Plan

### Phase 1: Database Schema
1. Create `task_pages` table
2. Create `task_page_statuses` table
3. Create `task_page_responses` table
4. Add `task_page_id` column to `cards`

### Phase 2: API Endpoints
1. Implement task page CRUD endpoints
2. Implement status endpoints
3. Implement response/evaluation endpoints
4. Add batch status endpoint

### Phase 3: Task API Library
1. Create `/static/js/task-api.js`
2. Define standard HTML template structure
3. Document task page conventions

### Phase 4: PWA Integration
1. Add task page view component
2. Add iframe rendering logic
3. Add IndexedDB stores for task pages
4. Update service worker to cache task pages

### Phase 5: Card Integration
1. Add `task_reference` card type
2. Update card display to show task status
3. Implement smart card generation based on status

### Phase 6: Content Migration
1. Convert complex existing cards to task pages
2. Keep simple cards as-is
3. Generate task reference cards for migrated content

---

## Example: Complete Flow

1. **User opens PWA** → sees card list with mixed cards
2. **Card shows**: "Kreislaufwirtschaft Übung" with badge "In Bearbeitung"
3. **User taps card** → PWA loads task page in iframe
4. **Task page renders** with user's previous progress (via status API)
5. **User completes exercise** → task page JS calls `TaskAPI.submitResponse()`
6. **User marks complete** → task page JS calls `TaskAPI.setStatus('completed')`
7. **User returns to cards** → card now shows "Abgeschlossen" badge
8. **Later**: LLM generates evaluation, stored in `task_page_responses.evaluation`
9. **Next session**: Card appears "Feedback verfügbar für Kreislaufwirtschaft"
10. **User opens task page** → sees evaluation via `TaskAPI.getEvaluation()`

---

## Open Questions

1. **Task page versioning**: How to handle updates to task page content without losing user progress?
2. **Partial completion**: Should task pages support saving partial responses (drafts)?
3. **Multi-device**: If user has multiple devices, how to handle status conflicts?
4. **Task page dependencies**: Can one task page require another to be completed first?