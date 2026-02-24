# Local-First Learning Platform Architecture

## Overview

A privacy-preserving, offline-first learning platform where:
- **Learning progress lives on the device** (IndexedDB)
- **Cards are open educational resources** (publicly downloadable)
- **Responses are anonymous** (linked only by device token)
- **Sync is manual and deliberate** (user-initiated)
- **Evaluations are delayed** (batch-generated, encourages thoughtful responses)

---

## Design Principles

### 1. Privacy-First
- No user accounts, no passwords, no PII
- Device token is not an identity - just a correlation key
- All personal learning data stays on device

### 2. Offline-First
- App works fully without network
- Responses queue locally until sync
- Cards cached in IndexedDB

### 3. Delayed Evaluation
- No instant feedback (prevents trial-and-error gaming)
- Evaluations generated in batch (via Claude CLI)
- User receives yesterday's evaluations during today's sync

### 4. Open Content
- Cards are openly downloadable by default
- Device-specific cards can be published by user
- Supports open educational resource model

### 5. Monetization-Ready
- Manual sync button = control point
- Paid tiers can unlock: more cards, faster evaluation, higher sync frequency

---

## Architecture

### Server (PostgreSQL)

```sql
-- Cards: open educational resources
CREATE TABLE cards (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    semantic_description TEXT NOT NULL,
    course_task_ref VARCHAR(255),
    card_html TEXT NOT NULL,
    response_schema JSONB NOT NULL,
    -- Visibility
    visibility VARCHAR(20) DEFAULT 'public',  -- 'public' | 'private'
    device_token VARCHAR(64),                  -- NULL for public, set for private
    -- Metadata
    card_type VARCHAR(20) DEFAULT 'learning', -- 'learning' | 'evaluation' | 'feedback_response'
    parent_response_id INTEGER,               -- Links evaluation to original response
    generation_batch VARCHAR(64)              -- Groups cards from same generation run
);

-- Responses: anonymous submissions
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,        -- Links to device, not identity
    responded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_content JSONB NOT NULL,
    -- Evaluation tracking
    evaluated BOOLEAN DEFAULT FALSE,
    evaluated_at TIMESTAMP,
    evaluation_card_id INTEGER                -- Links to generated evaluation card
);

-- Feedback: optional card ratings
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    response_id INTEGER REFERENCES responses(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    comment TEXT
);

-- Indexes
CREATE INDEX idx_cards_device_token ON cards(device_token);
CREATE INDEX idx_cards_visibility ON cards(visibility);
CREATE INDEX idx_responses_device_token ON responses(device_token);
CREATE INDEX idx_responses_not_evaluated ON responses(evaluated) WHERE evaluated = FALSE;
```

### PWA (IndexedDB)

```javascript
// IndexedDB Schema
const DB_NAME = 'sociology-learning';
const DB_VERSION = 1;

const stores = {
    // Device identity (generated once)
    config: {
        keyPath: 'key',
        // Records: { key: 'device_token', value: 'abc123...' }
    },

    // Cached cards from server
    cards: {
        keyPath: 'id',
        indexes: ['card_type', 'visibility']
        // Full card objects from server
    },

    // Local progress (never synced to server)
    progress: {
        keyPath: 'card_id',
        // { card_id, status, scheduled_for, queued_at, completed_at }
    },

    // Local notes (never synced to server)
    notes: {
        keyPath: 'card_id',
        // { card_id, content, updated_at }
    },

    // Pending responses (waiting for sync)
    pending_responses: {
        keyPath: 'local_id',
        autoIncrement: true,
        // { card_id, response_content, responded_at, feedback }
    },

    // Sync history
    sync_log: {
        keyPath: 'id',
        autoIncrement: true,
        // { synced_at, responses_sent, cards_received }
    }
};
```

---

## Data Flow

### 1. First Visit
```
┌─────────────┐
│   Device    │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────┐
│  Generate device_token           │
│  crypto.randomUUID()             │
│  Store in IndexedDB              │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  Fetch public cards              │
│  GET /api/cards?visibility=public│
│  Cache in IndexedDB              │
└──────────────────────────────────┘
```

### 2. Learning (Offline-Capable)
```
┌─────────────────────────────────────────────────────────────┐
│                     ALL LOCAL                                │
├─────────────────────────────────────────────────────────────┤
│  1. Load card from IndexedDB                                │
│  2. User answers                                            │
│  3. Save response to pending_responses (IndexedDB)          │
│  4. Update progress in IndexedDB                            │
│  5. Load next card from IndexedDB                           │
└─────────────────────────────────────────────────────────────┘
```

### 3. Manual Sync (User-Initiated)
```
┌─────────────┐                              ┌─────────────┐
│   Device    │                              │   Server    │
└──────┬──────┘                              └──────┬──────┘
       │                                            │
       │  POST /api/sync                            │
       │  {                                         │
       │    device_token: "abc123",                 │
       │    responses: [...pending],                │
       │    last_sync: "2024-02-23T10:00:00Z"      │
       │  }                                         │
       │ ──────────────────────────────────────────>│
       │                                            │
       │                                            │ Store responses
       │                                            │
       │  {                                         │
       │    success: true,                          │
       │    new_cards: [...],      ◄────────────────│ Return cards
       │    stats: { sent: 5, received: 3 }         │ created since
       │  }                                         │ last_sync
       │ <──────────────────────────────────────────│
       │                                            │
       ▼                                            │
┌──────────────────────────────────┐                │
│  Clear pending_responses         │                │
│  Add new_cards to IndexedDB      │                │
│  Log sync in sync_log            │                │
└──────────────────────────────────┘
```

### 4. Evaluation Generation (Server-Side, via Claude CLI)
```
┌─────────────────────────────────────────────────────────────┐
│                   CLAUDE CLI (Periodic)                      │
├─────────────────────────────────────────────────────────────┤
│  1. Query: SELECT * FROM responses WHERE evaluated = FALSE  │
│  2. Group by device_token                                   │
│  3. Generate evaluation cards for each response             │
│  4. INSERT new cards (card_type='evaluation',               │
│                       device_token=response.device_token,   │
│                       parent_response_id=response.id)       │
│  5. UPDATE responses SET evaluated = TRUE                   │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### Public Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cards?visibility=public` | Get all public cards |
| GET | `/api/cards/:id` | Get single card (if public) |

### Device-Token Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/sync` | Upload responses, get new cards |
| GET | `/api/cards?device_token=xxx` | Get public + private cards for device |
| POST | `/api/cards/:id/publish` | Make private card public |

### Sync Request/Response

```javascript
// Request
POST /api/sync
{
    "device_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "responses": [
        {
            "card_id": 42,
            "response_content": { "answer": "..." },
            "responded_at": "2024-02-24T09:15:00Z",
            "feedback": { "rating": 4, "comment": "Good card" }  // optional
        }
    ],
    "last_sync": "2024-02-23T10:00:00Z"  // or null for first sync
}

// Response
{
    "success": true,
    "responses_received": 3,
    "new_cards": [
        { "id": 101, "card_html": "...", ... },
        { "id": 102, "card_html": "...", ... }
    ],
    "stats": {
        "total_responses": 47,
        "pending_evaluations": 3,
        "cards_available": 52
    }
}
```

---

## UI Components

### Sync Button

Located in header, shows sync status:

```
┌────────────────────────────────────────────┐
│  Soziologie              [🔄 3 pending]    │
└────────────────────────────────────────────┘
```

States:
- `🔄 N pending` - Has responses waiting to sync
- `✓ Synced` - All caught up
- `↻ Syncing...` - Sync in progress
- `⚠ Offline` - No network (can still learn)

### Private Card Indicator

Cards with `visibility: 'private'` show lock icon:

```
┌────────────────────────────────────────────┐
│                                      [🔒]  │
│  Your evaluation for yesterday's           │
│  response about Kreislaufwirtschaft...     │
│                                            │
│  [Tap 🔒 to make this card public]         │
└────────────────────────────────────────────┘
```

### Progress Stats (Local)

```
┌────────────────────────────────────────────┐
│  Today: 5 completed                        │
│  Pending: 12 cards                         │
│  Scheduled: 3 for tomorrow                 │
│                                            │
│  [Last sync: 2 hours ago]                  │
└────────────────────────────────────────────┘
```

---

## Monetization Hooks

The manual sync model enables tiered access:

| Feature | Free | Pro |
|---------|------|-----|
| Public cards | ✓ | ✓ |
| Sync frequency | 1x/day | Unlimited |
| Evaluation depth | Basic | Detailed |
| New cards/week | 5 | Unlimited |
| Priority evaluation | - | ✓ |

Implementation:
- Sync endpoint checks device_token against subscription table
- Returns appropriate cards based on tier
- Rate limiting per device_token

---

## Migration Plan

### Phase 1: Simplify Server
1. Remove: `users`, `user_cards`, `invites` tables
2. Add: `device_token` and `visibility` columns to cards
3. Add: `device_token` column to responses
4. Create new `feedback` table

### Phase 2: Add IndexedDB to PWA
1. Create IndexedDB schema
2. Generate and persist device_token
3. Cache cards locally
4. Store progress/notes locally

### Phase 3: Implement Local-First Learning
1. Load cards from IndexedDB
2. Queue responses locally
3. Update progress locally
4. Remove server dependency for learning flow

### Phase 4: Add Manual Sync
1. Add sync button to UI
2. Implement `/api/sync` endpoint
3. Upload pending responses
4. Download new cards
5. Clear pending queue

### Phase 5: Card Visibility
1. Add lock icon for private cards
2. Implement publish action
3. Filter cards by visibility + device_token

---

## Security Considerations

### Device Token
- Generated client-side: `crypto.randomUUID()`
- Not an authentication token - just correlation
- Acceptable security for non-sensitive learning data
- Leaked token = someone could see your evaluations (low risk)

### Data Exposure
- Public cards: Intentionally open
- Private cards: Only fetchable with device_token
- Responses: No PII, only learning content
- Progress/Notes: Never leave device

### Abuse Prevention
- Rate limit sync endpoint per device_token
- Rate limit response submissions
- Monitor for suspicious patterns

---

## File Structure After Implementation

```
app.py                  # Simplified: cards, responses, feedback, sync
templates/
  index.html            # PWA with IndexedDB
static/
  js/
    db.js               # IndexedDB wrapper
    sync.js             # Sync logic
    app.js              # Main app logic
  sw.js                 # Service worker (offline support)
docs/
  LOCAL-FIRST-ARCHITECTURE.md  # This document
```

---

## Open Questions (For Later)

1. **Backup/Export:** Format for exporting local data? JSON? Integration with cloud storage?
2. **Device Migration:** How to move learning progress to new device?
3. **Conflict Resolution:** What if same device_token syncs from two browsers?
4. **Card Versioning:** How to handle card updates/corrections?
