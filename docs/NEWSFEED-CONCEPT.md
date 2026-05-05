# Newsfeed Feature - Implementation Concept

## Overview

The newsfeed feature adds a third tab to the commute-cards PWA, providing a shared social feed where users can engage with posts through likes, comments, and visibility controls. The feed is designed to increase engagement with actualities, historical fun facts, user progress highlights, and interactive quizzes.

## Architecture

### Database Schema

Three new tables support the newsfeed feature:

```sql
-- Feed items - shared content posts
CREATE TABLE feed_items (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author_device_token VARCHAR(64),
    author_display_name VARCHAR(100),
    item_type VARCHAR(50) DEFAULT 'post',
    content_html TEXT NOT NULL,
    reaction_schema JSONB DEFAULT '{}',
    course_id INTEGER REFERENCES courses(id),
    tags TEXT[],
    metadata JSONB DEFAULT '{}'
);

-- Feed reactions - likes, comments, votes
CREATE TABLE feed_reactions (
    id SERIAL PRIMARY KEY,
    feed_item_id INTEGER REFERENCES feed_items(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,
    display_name VARCHAR(100),
    reaction_type VARCHAR(50) NOT NULL,
    reaction_content JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Per-user visibility controls
CREATE TABLE feed_item_user_state (
    id SERIAL PRIMARY KEY,
    feed_item_id INTEGER REFERENCES feed_items(id) ON DELETE CASCADE,
    device_token VARCHAR(64) NOT NULL,
    hidden BOOLEAN DEFAULT FALSE,
    show_after DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(feed_item_id, device_token)
);
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/feed` | GET | Get paginated feed items with reactions |
| `/api/feed/items` | POST | Create a new feed item |
| `/api/feed/items/:id` | GET | Get a single feed item |
| `/api/feed/items/:id/react` | POST | Add reaction (like toggles, comments add) |
| `/api/feed/items/:id/react/:rid` | DELETE | Remove own reaction |
| `/api/feed/items/:id/visibility` | POST | Set hide/show_later/show |

### Query Parameters

**GET /api/feed:**
- `device_token` - Required for personalized feed (filters hidden items)
- `limit` - Items per page (default 20, max 50)
- `offset` - Pagination offset
- `course` - Filter by course slug

## Frontend Components

### feedApp() Alpine Component

Located in `/static/js/app.js`, the `feedApp()` component handles:
- Loading and paginating feed items
- Like toggle (single-click to like/unlike)
- Comment submission
- Visibility controls (hide forever, show in N days)
- Display name management (stored in localStorage)

### UI Elements

1. **Feed Tab** - Middle tab in bottom navigation
2. **Feed Header** - "Feed" title with refresh button
3. **Display Name Prompt** - Appears if user hasn't set a name
4. **Feed Items** - Cards with:
   - Author avatar (first letter)
   - Author name and timestamp
   - Content HTML
   - Like/comment buttons with counts
   - Three-dot menu for visibility controls
5. **Comments Section** - Expandable, shows existing comments and input form
6. **Load More** - Infinite scroll pagination

## Content Types

The `item_type` field supports extensible content types:

| Type | Description |
|------|-------------|
| `post` | Standard text/HTML post |
| `quiz` | Interactive quiz (uses reaction_schema) |
| `poll` | User voting (uses reaction_schema) |
| `progress` | User achievement highlight |
| `fact` | Historical/fun fact |

## Reaction Schema

The `reaction_schema` JSONB field defines available reactions for extensible content:

```json
{
  "reactions": {
    "like": { "enabled": true },
    "comment": { "enabled": true },
    "vote": {
      "enabled": true,
      "options": ["Option A", "Option B", "Option C"]
    }
  }
}
```

## User Identity

- Anonymous users with `device_token` (UUID)
- Optional `display_name` stored in localStorage
- Shared reactions visible to all users

## Feed Algorithm (MVP)

Simple chronological ordering with user-controlled visibility:
1. Exclude items user has hidden
2. Exclude items with `show_after` in the future
3. Order by `created_at DESC`

Future enhancements could include:
- Engagement-based ranking
- Course/tag relevance
- User preference learning

## Content Generation

MVP approach:
- LLM generates posts on-demand
- Admin interface for content creation (future)
- No scheduling system initially

## Files Modified

- `app.py` - Database tables and API endpoints
- `static/js/app.js` - feedApp() component
- `templates/index.html` - Feed section and tab navigation

## Future Enhancements

1. **Admin Interface** - Web UI for creating posts
2. **Notifications** - Alert users to new comments on their content
3. **Rich Content** - Image uploads, embedded media
4. **Moderation** - Report/flag inappropriate content
5. **Analytics** - Track engagement metrics
6. **Local-first** - Cache feed items in IndexedDB
