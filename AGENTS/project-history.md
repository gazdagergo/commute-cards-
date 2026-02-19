# Chinese Learning PWA - Project History

## Overview

A mobile-first Progressive Web App for learning Chinese through stories and flashcards. Built with Flask, PostgreSQL, Alpine.js, and deployed on Fly.io.

**Live URL:** https://chinese-learning-pwa.fly.dev/

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** PostgreSQL on Fly.io
- **Frontend:** Jinja2 templates, Alpine.js for interactivity
- **Styling:** Vanilla CSS, mobile-first
- **Deployment:** Fly.io with Docker
- **External Libraries:**
  - Alpine.js (reactive UI)
  - Hanzi Writer (stroke order animations)

## Database Schema

```sql
-- Stories table
CREATE TABLE stories (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Flashcards table
CREATE TABLE flashcards (
    id SERIAL PRIMARY KEY,
    chinese VARCHAR(50) NOT NULL,
    english VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many relationship between flashcards and stories
CREATE TABLE flashcard_stories (
    flashcard_id INTEGER REFERENCES flashcards(id) ON DELETE CASCADE,
    story_id INTEGER REFERENCES stories(id) ON DELETE CASCADE,
    PRIMARY KEY (flashcard_id, story_id)
);
```

## Features Implemented

### Stories
- List all stories on home page
- View individual story
- Add new stories
- **Practice mode** (toggle on story page):
  - Text becomes scrollable (2-3 lines visible)
  - Opacity slider to hide/reveal text
  - Textarea to write from memory
  - Check button with similarity percentage

### Flashcards
- List all flashcards (shows Chinese + English only)
- Add new flashcards (Chinese, English, description)
- Edit existing flashcards
- **Detail view with Hanzi Writer:**
  - Tap individual characters to see stroke animation
  - Works with multi-character words
  - Description/notes section
- **Link flashcards to stories:**
  - Checkbox multi-select when adding/editing
  - Vocabulary badges appear on story page
  - Back button navigates to story when coming from story context

### PWA Support
- Web manifest for "Add to Home Screen"
- iOS standalone mode (no address bar)
- Apple touch icons
- Theme color integration

## Key Files

```
chinese-learning-pwa/
├── app.py                      # Flask routes and database
├── Dockerfile                  # Docker build config
├── fly.toml                    # Fly.io config
├── requirements.txt            # Python dependencies
├── static/
│   ├── manifest.json          # PWA manifest
│   ├── icon-192.png           # App icon
│   ├── icon-512.png           # App icon (large)
│   └── apple-touch-icon.png   # iOS icon
└── templates/
    ├── index.html             # Home - story list
    ├── story.html             # Story view with practice toggle
    ├── add.html               # Add story form
    ├── flashcards.html        # Flashcard list
    ├── flashcards_form.html   # Add/edit flashcard form
    ├── flashcard_detail.html  # Flashcard with Hanzi Writer
    └── practice.html          # (legacy, kept for compatibility)
```

## Development History

### Phase 1: Initial Setup
- Started with fly-apps/python-hellofly-flask template
- Configured PostgreSQL on Fly.io
- Switched from psycopg2 to psycopg v3 (Python 3.13 compatibility)
- Simplified database connections (no pooling, direct connect)

### Phase 2: Core Features
- Added stories CRUD
- Created story detail view
- Added writing practice mode with opacity slider
- Used Alpine.js for reactive UI (moved JS to script tags to avoid Jinja2 conflicts)

### Phase 3: Flashcards
- Added flashcards table and routes
- Created add/edit forms
- Integrated Hanzi Writer for stroke order animations
- Simplified animation: tap-to-play per character (no auto-start)

### Phase 4: Story-Flashcard Integration
- Added junction table for many-to-many relationship
- Checkbox multi-select for linking flashcards to stories
- Vocabulary badges on story pages
- Dynamic back button (returns to story when navigating from story context)

### Phase 5: UI Improvements
- Merged practice mode into story page with toggle switch
- Made text box scrollable in practice mode
- Added PWA manifest and iOS meta tags
- Standalone mode without browser address bar

## Design Decisions

1. **No TTS integration:** User discovered iOS native speech works well for Chinese text
2. **No flashcard review mode:** Simple vocabulary list is sufficient for MVP
3. **Tap-to-animate:** Each Hanzi character animates on tap (simpler than auto-play)
4. **Unified story/practice view:** Toggle instead of separate page
5. **Mobile-first:** Designed primarily for iPhone usage

## Future Ideas (mentioned but not implemented)
- Persist textarea content when navigating to flashcard and back
- Delete functionality for flashcards/stories
- More sophisticated review/quiz mode
- Interactive stroke practice with Hanzi Writer

## Deployment Commands

```bash
# Deploy to Fly.io
fly deploy

# Check logs
fly logs

# Check app status
fly status

# Connect to database
fly postgres connect -a chinese-learning-pwa-db
```

## Local Development

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://..."

# Run locally
python app.py
```

The app runs on port 8080 and initializes the database tables on startup.
