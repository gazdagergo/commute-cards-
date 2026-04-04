# Task Pages Implementation Plan

## Overview

Incremental implementation of the Task Pages architecture. Each phase is independently deployable and testable.

**Branch:** `feature/task-pages`
**Deploy target:** Staging first, then production after validation

---

## Phase 1: Database Schema & Migrations

**Goal:** Add database tables for task pages with reversible migrations.

**Changes:**
- Create `task_pages` table
- Create `task_page_statuses` table
- Create `task_page_responses` table
- Add `task_page_id` column to `cards` table
- Create migration script with UP and DOWN functions

**Files:**
- `migrations/001_task_pages.py` (new)
- `app.py` (add migration runner)

**Testing:**
```bash
# Run UP migration
python migrations/001_task_pages.py up

# Verify tables exist
fly postgres connect -a sociology-learning-pwa-db
\dt task_*

# Run DOWN migration (rollback)
python migrations/001_task_pages.py down
```

**Deployable:** Yes (backend only, no breaking changes)

---

## Phase 2: Basic Task Page API

**Goal:** CRUD endpoints for task pages and status management.

**Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/task-pages` | List task pages (with filters) |
| GET | `/api/task-pages/:id` | Get task page with current status |
| GET | `/api/task-pages/:id/html` | Get raw HTML for iframe |
| POST | `/api/task-pages/:id/status` | Update status for device |
| GET | `/api/task-pages/:id/status` | Get status for device |

**Files:**
- `app.py` (add endpoints)

**Testing:**
```bash
# Create a test task page manually in DB first
# Then test endpoints:
curl https://staging.../api/task-pages
curl https://staging.../api/task-pages/test-page-1
curl -X POST https://staging.../api/task-pages/test-page-1/status \
  -H "X-Device-Token: test123" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

**Deployable:** Yes (new endpoints, no breaking changes)

---

## Phase 3: Response & Evaluation API

**Goal:** Endpoints for task page submissions and evaluations.

**Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/task-pages/:id/response` | Submit response |
| GET | `/api/task-pages/:id/responses` | Get all responses for device |
| GET | `/api/task-pages/:id/evaluation` | Get latest evaluation |
| POST | `/api/task-pages/batch-status` | Get statuses for multiple pages |

**Files:**
- `app.py` (add endpoints)

**Testing:**
```bash
# Submit a response
curl -X POST https://staging.../api/task-pages/test-page-1/response \
  -H "X-Device-Token: test123" \
  -H "Content-Type: application/json" \
  -d '{"response_content": {"answer": "test"}}'

# Get responses
curl https://staging.../api/task-pages/test-page-1/responses \
  -H "X-Device-Token: test123"
```

**Deployable:** Yes (new endpoints, no breaking changes)

---

## Phase 4: Task API Library

**Goal:** Client-side JS library for task pages to communicate with server.

**Files:**
- `static/js/task-api.js` (new)

**Contents:**
```javascript
// Provides: TaskAPI.setStatus(), TaskAPI.submitResponse(),
//           TaskAPI.getEvaluation(), TaskAPI.getStatus()
```

**Testing:**
- Create a minimal test HTML page that loads task-api.js
- Verify API calls work from browser console

**Deployable:** Yes (static file, no integration yet)

---

## Phase 5: PWA IndexedDB Updates

**Goal:** Add local storage for task pages in PWA.

**Changes:**
- Bump DB_VERSION to 3
- Add `task_pages` store
- Add `task_page_statuses` store
- Add `pending_task_updates` store
- Add db.js functions: `saveTaskPage()`, `getTaskPage()`, `updateTaskPageStatus()`, etc.

**Files:**
- `static/js/db.js` (update)

**Testing:**
- Open PWA in browser
- Check IndexedDB in DevTools shows new stores
- Test functions from console

**Deployable:** Yes (PWA auto-upgrades IndexedDB)

---

## Phase 6: PWA Task Page View

**Goal:** Render task pages in iframe within PWA.

**Changes:**
- Add task page view component in Alpine.js
- Add iframe rendering with device token injection
- Add navigation: card → task page → back
- Add route handling for task pages

**Files:**
- `static/js/app.js` (update)
- `templates/index.html` (update)

**Testing:**
- Navigate to a task page from card
- Verify iframe renders
- Verify device token is injected
- Verify back navigation works

**Deployable:** Yes (new view, existing cards unaffected)

---

## Phase 7: Card Integration

**Goal:** Cards can reference task pages and show status.

**Changes:**
- Handle `task_page_id` on cards
- Display status badge on task-reference cards
- Fetch task page status when displaying card
- Add `task_reference` card type

**Files:**
- `static/js/app.js` (update)
- `templates/index.html` (update)

**Testing:**
- Create a card with `task_page_id` reference
- Verify status badge displays
- Verify tapping opens task page view

**Deployable:** Yes (backwards compatible)

---

## Phase 8: Sample Task Page & E2E Test

**Goal:** Create a real task page and test full flow.

**Changes:**
- Create sample task page HTML
- Insert script for sample content
- Document task page creation workflow

**Files:**
- `scripts/insert_sample_task_page.py` (new)
- `docs/TASK-PAGE-CREATION-GUIDE.md` (new)

**Testing:**
1. Run insert script
2. Open PWA
3. See card referencing task page
4. Open task page
5. Complete task, submit response
6. Mark as completed
7. Verify status updates on card

**Deployable:** Yes (content only)

---

## Migration Scripts Structure

```
migrations/
├── __init__.py
├── runner.py           # Migration runner utility
└── 001_task_pages.py   # Task pages schema
```

### Migration Template

```python
"""
Migration: 001_task_pages
Description: Add task pages tables
"""

def up(conn):
    """Apply migration"""
    with conn.cursor() as cur:
        # Create tables...
        pass
    conn.commit()

def down(conn):
    """Rollback migration"""
    with conn.cursor() as cur:
        # Drop tables in reverse order...
        pass
    conn.commit()

if __name__ == "__main__":
    import sys
    from runner import run_migration
    run_migration(__file__, sys.argv[1] if len(sys.argv) > 1 else "up")
```

---

## Rollback Procedure

If issues occur after deployment:

```bash
# 1. Rollback code
git revert <commit-hash>
fly deploy --config fly.staging.toml

# 2. Rollback database (if needed)
fly ssh console -a sociology-learning-pwa-staging
cd /app
python migrations/001_task_pages.py down
```

---

## Progress Tracking

| Phase | Status | Commit | Deployed Staging | Deployed Prod |
|-------|--------|--------|------------------|---------------|
| 1. DB Schema | ⬜ Pending | - | - | - |
| 2. Basic API | ⬜ Pending | - | - | - |
| 3. Response API | ⬜ Pending | - | - | - |
| 4. Task API Lib | ⬜ Pending | - | - | - |
| 5. IndexedDB | ⬜ Pending | - | - | - |
| 6. Task View | ⬜ Pending | - | - | - |
| 7. Card Integration | ⬜ Pending | - | - | - |
| 8. Sample & E2E | ⬜ Pending | - | - | - |

---

## Open Questions (Resolved)

1. **Task page versioning** → DB migrations handle schema; page content versions tracked via `updated_at`
2. **Partial completion** → Draft mode supported via status = 'draft' + local form state
3. **Multi-device** → Ignored for now (edge case)
4. **Task dependencies** → Each task page handles own dependency logic via API calls