# Authentication Concept: Invite-Based PWA Access

## Overview

A lightweight authentication system for sharing the learning app with invited users. Uses one-time invite links with permanent device tokens, optimized for PWA usage.

## Goals

- Only invited users can access the app
- Each user sees their own responses and card schedules
- Cards (content) are shared; card state is per-user
- No passwords to remember or share
- Works seamlessly with PWA "Add to Home Screen"

## User Journey

```
1. Admin generates invite link for Anna
   → https://sociology-learning-pwa.fly.dev/invite/abc123xyz

2. Anna clicks the link (in browser)
   → Backend validates token, marks as used
   → Creates user record with new auth_token
   → Stores auth_token in localStorage
   → Shows PWA installation instructions

3. Anna adds app to home screen
   → PWA inherits localStorage from browser
   → auth_token persists with PWA

4. Anna uses the app
   → All API requests include auth_token
   → Backend identifies user, returns their data

5. If Anna loses access (deletes PWA, new phone)
   → Admin generates new invite link
```

## Database Schema Changes

### New Tables

```sql
-- Invite links (one-time use)
CREATE TABLE invites (
    id SERIAL PRIMARY KEY,
    token VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(255),
    label VARCHAR(255),              -- e.g., "Anna's invite"
    used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP,
    used_by_user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users (created when invite is claimed)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(255),
    auth_token VARCHAR(64) UNIQUE NOT NULL,
    invite_id INTEGER REFERENCES invites(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP
);

-- Per-user card state (replaces card-level status)
CREATE TABLE user_cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER REFERENCES cards(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active',
    scheduled_for DATE,
    queued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                               -- User's personal notes for this card
    UNIQUE(user_id, card_id)
);
```

### Modified Tables

```sql
-- responses: add user_id
ALTER TABLE responses ADD COLUMN user_id INTEGER REFERENCES users(id);

-- cards: remove per-user fields (moved to user_cards)
-- status, scheduled_for, queued_at become shared defaults or removed
```

## API Changes

### New Endpoints

```
GET  /invite/<token>     → Claim invite, create user, redirect to app
POST /api/auth/whoami    → Return current user info (or 401)
```

### Modified Endpoints

All existing endpoints check `Authorization: Bearer <auth_token>` header:

```
GET  /api/next-card      → Returns next card for current user
POST /api/response       → Records response for current user
POST /api/schedule       → Updates schedule for current user
GET  /api/stats          → Returns stats for current user
```

### Admin Endpoints (future)

```
POST /admin/invites      → Generate new invite link
GET  /admin/invites      → List all invites
GET  /admin/users        → List all users
```

## Frontend Changes

### Token Storage

```javascript
// On invite claim (set by backend or frontend)
localStorage.setItem('auth_token', 'xxx...');

// On every API request
fetch('/api/next-card', {
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
    }
});

// On app load, check if authenticated
if (!localStorage.getItem('auth_token')) {
    // Show "need invite" message
}
```

### PWA Installation Flow

After claiming invite, show installation prompt:

```html
<div class="install-instructions">
    <h2>Fast fertig!</h2>
    <p>Füge die App zu deinem Homescreen hinzu:</p>

    <div class="ios-instructions">
        <p>1. Tippe auf <strong>Teilen</strong> (□↑)</p>
        <p>2. Wähle <strong>"Zum Home-Bildschirm"</strong></p>
    </div>

    <div class="android-instructions">
        <p>1. Tippe auf <strong>⋮</strong> (Menü)</p>
        <p>2. Wähle <strong>"App installieren"</strong></p>
    </div>
</div>
```

## Security Considerations

| Aspect | Approach |
|--------|----------|
| Invite token | 64-char random string, one-time use |
| Auth token | 64-char random string, permanent until revoked |
| Token storage | localStorage (acceptable for this use case) |
| Transport | HTTPS only (Fly.io default) |
| Token in URL | Invite token only, immediately invalidated |

### Risks & Mitigations

1. **Invite link intercepted before use**
   - Low risk for direct sharing (Signal, WhatsApp)
   - Mitigation: Links expire after 7 days even if unused

2. **Auth token stolen from device**
   - Requires physical device access
   - Mitigation: User can request new invite, old token revoked

3. **localStorage cleared**
   - User loses access
   - Mitigation: Easy to generate new invite

## Token Generation

```python
import secrets

def generate_token():
    return secrets.token_urlsafe(48)  # 64 chars, URL-safe

# Example output: "a3Bf9xK2mN7pQ1wE4rT8yU0iO5lH6jD9..."
```

## Migration Path

### Phase 1: Add auth without breaking existing usage
1. Add tables (invites, users, user_cards)
2. Create "default" user for existing responses
3. Auth token optional (empty = default user)

### Phase 2: Require auth
1. Generate invites for known users
2. Migrate existing card states to user_cards (including notes from cards.notes)
3. Require auth token on all API calls
4. Update /api/card/:id/notes to use user_cards.notes

### Phase 3: Admin features
1. Add admin role
2. Build invite management UI
3. User activity dashboard

## Multi-Subject Support

Users can study different subjects (sociology, math, etc.) within the same app. Subject access is controlled at invite time.

### Schema

```sql
-- Available subjects
CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(50) UNIQUE NOT NULL,    -- 'sociology', 'math', 'physics'
    name VARCHAR(255) NOT NULL,          -- 'Soziologie B1', 'Linear Algebra'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Which subjects a user can access (set at invite time)
CREATE TABLE user_subjects (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, subject_id)
);

-- Cards belong to a subject
ALTER TABLE cards ADD COLUMN subject_id INTEGER REFERENCES subjects(id);
CREATE INDEX idx_cards_subject ON cards(subject_id);
```

### Invite Flow with Subjects

When generating an invite, specify which subjects the user can access:

```sql
-- Invite includes subject access
CREATE TABLE invite_subjects (
    invite_id INTEGER REFERENCES invites(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    PRIMARY KEY (invite_id, subject_id)
);
```

```
Admin creates invite:
  → token: "abc123"
  → subjects: [math, physics]

Anna claims invite:
  → user created
  → user_subjects populated from invite_subjects
  → Anna can access math & physics cards only
```

### User Experience

1. **Login/App Open**: User sees subject picker (only eligible subjects shown)
2. **Subject Selection**: Stored in localStorage as `active_subject`
3. **Card Display**: Only cards from active subject
4. **Switching**: User can switch subjects anytime (within their eligible list)

### API Changes

```
GET  /api/subjects           → Returns subjects current user can access
POST /api/subjects/active    → Set active subject for session
GET  /api/next-card          → Filters by active subject
```

### Frontend Subject Picker

```javascript
// On app load
const subjects = await fetch('/api/subjects').then(r => r.json());

if (subjects.length === 1) {
    // Auto-select if only one subject
    setActiveSubject(subjects[0].slug);
} else {
    // Show picker
    showSubjectPicker(subjects);
}
```

```html
<!-- Subject picker UI -->
<div class="subject-picker">
    <h2>Was möchtest du lernen?</h2>
    <button @click="setSubject('sociology')">Soziologie</button>
    <button @click="setSubject('math')">Mathematik</button>
</div>
```

### Example Data

```
Subjects:
  id=1, slug='sociology', name='Soziologie B1'
  id=2, slug='math', name='Lineare Algebra'
  id=3, slug='physics', name='Physik I'

Users:
  id=1, name='You'      → subjects: [sociology]
  id=2, name='Anna'     → subjects: [math, physics]
  id=3, name='Peter'    → subjects: [sociology, math]

Cards:
  id=1, subject=sociology, "Was ist Sozialisation?"
  id=2, subject=sociology, "Policy vs Polity"
  id=3, subject=math, "Explain eigenvalues"
  id=4, subject=physics, "Newton's laws"

What each user sees:
  You   → cards 1, 2
  Anna  → cards 3, 4
  Peter → cards 1, 2, 3
```

### Card Generation Workflow

Each subject can have its own:
- `CARD_CONVENTION.md` (or shared)
- Materials folder / corpus
- PDF index in Pinecone (namespaced by subject)

```
sociology/
  materials/
  CARD_CONVENTION.md

math/
  materials/
  CARD_CONVENTION.md
```

When generating cards via Claude:
```
"Generate 5 math cards following math/CARD_CONVENTION.md,
 set subject_id to the math subject ID"
```

## Open Questions

- [ ] Should auth_token rotate periodically?
- [ ] How to handle "shared" reflection cards (based on user's own responses)?
- [ ] Multi-device support: one invite per device, or allow multiple?
- [ ] Offline mode: how to sync when back online?
- [ ] Can users request access to additional subjects? (Or admin-only)

## Alternatives Considered

| Option | Why not |
|--------|---------|
| Google OAuth | Registration overhead, unverified app warning |
| Email/password | Can be shared, password management burden |
| Magic links (each login) | Requires email on every session, poor UX |
| No auth | Can't separate user data |

## References

- [Flask-Login documentation](https://flask-login.readthedocs.io/)
- [PWA localStorage behavior](https://web.dev/learn/pwa/offline-data/)
- [Secure token generation in Python](https://docs.python.org/3/library/secrets.html)