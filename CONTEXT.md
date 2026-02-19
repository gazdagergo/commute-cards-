# Chinese Learning PWA — Context Handover for Claude Code

## What this project is
A PWA for memorizing Chinese short readings (tales). Two core features: listening (TTS) and writing practice (character drawing). Mobile-first, designed for iPhone.

## Tech Stack
- **Backend:** Python Flask
- **Templates:** Jinja2
- **Frontend JS:** Alpine.js
- **UI:** Plain CSS for now (PineUI was considered but documentation is sparse)
- **Database:** PostgreSQL on Fly.io
- **Hosting:** Fly.io (Frankfurt region, closest to Budapest)
- **TTS:** Google Cloud TTS (paid API, ~$4/1M chars) — to be integrated in Iteration 3

## Decisions Made (with reasoning)

### TTS granularity: Sentence-level
- Character-level would require 200+ manual timestamps per story — too much work
- Sentence-level: click anywhere in a sentence → plays that sentence
- 5-10 timestamps per story, manageable

### TTS provider: Paid API (Google Cloud TTS or similar)
- Browser Web Speech API is terrible for Chinese
- Usage is ~2-3 stories/month, so cost is literally pennies
- Google Cloud TTS or Azure preferred for price/quality ratio

### Audio caching: No caching for MVP
- Always-online for MVP (simpler)
- 2-3 stories/month = negligible API cost even with repeated playback
- Caching is a post-MVP feature

### Writing practice scope: Sentence-level, choose-your-sentence
- User sees full text, clicks any sentence to practice writing it
- Uses Hanzi Writer library (standard choice: stroke order animation, quiz mode, hint levels)
- Can repeat difficult sentences multiple times
- Not sequential forced order — user picks what to practice

### Learning workflow: Memorization through active recall
- **Reading/Listening mode:** See full text → tap sentence → hear it → try to repeat
- **Writing practice mode:** Hide text → try to write from memory → peek (hint) button reveals text → hide again → continue
- Translation/dictionary features are post-MVP

### Device: iPhone (mobile-first)
- Touch drawing with finger (natural for Hanzi Writer)
- Portrait orientation
- Smaller screen layout

### Hosting: Fly.io
- Frankfurt region (Budapest proximity)
- $5/month free credit covers everything
- Postgres: Development tier, scale-to-zero enabled
- Credit card on file but should cost $0 for this usage

## Iteration Plan

### ✅ Iteration 0: Infrastructure POC (CURRENT — IN PROGRESS)
- Flask app deployed on Fly.io
- Connected to Fly.io Postgres
- One table: `stories` (id, title, text, created_at)
- Index page lists stories, detail page shows story
- Alpine.js show/hide toggle on story detail (proof of concept)
- One seeded test story in Chinese
- **Status:** All files created, venv set up locally, need to run `fly launch`

### Iteration 1: Text storage + upload (next)
- Form to paste Chinese text + title
- Store in Postgres
- Display in list

### Iteration 2: Sentence segmentation
- Split text on 。！？
- Each sentence in a clickable `<span>`
- Click → highlight (no audio yet)

### Iteration 3: TTS integration
- Google Cloud TTS API setup
- Backend endpoint: `/tts?text=...` → returns audio
- Click sentence → fetch TTS → play in browser

### Iteration 4: Basic writing mode
- Hanzi Writer library integration
- "Practice writing" page for a story
- Click sentence → write characters sequentially
- Stroke order hints visible

### Iteration 5: Hide/reveal mechanism
- "Hide text" button → text blurred/hidden
- "Show hint" button → reveals text temporarily
- Core memorization loop complete

### Post-MVP (not yet planned in detail)
- Audio caching
- Translation/dictionary lookups
- Pinyin display
- Vocabulary tracking

## Current File Structure
```
chinese-learning-pwa/
├── app.py                  # Flask app, DB connection, routes, init_db
├── Dockerfile              # Python 3.12 slim, gunicorn, init_db on startup
├── requirements.txt        # Flask, gunicorn, psycopg2-binary, python-dotenv
├── .env.example            # DATABASE_URL template
├── .gitignore
├── templates/
│   ├── index.html          # Story list, Alpine.js, basic CSS
│   └── story.html          # Story detail, show/hide toggle with Alpine.js
└── .venv/                  # Local virtual environment (gitignored)
```

## Key Technical Details
- Database connection uses `psycopg` v3 connection pool (ConnectionPool, 1-5 connections)
- `init_db()` creates tables + seeds one test story if empty — runs on startup via Dockerfile CMD
- Fly.io sets `DATABASE_URL` environment variable automatically when Postgres is attached
- Health check at `/health` verifies DB connectivity
- Gunicorn runs with 2 workers in production
- Alpine.js loaded from CDN (jsdelivr)

## Next Steps Right Now
1. Run `fly launch` (venv is already active, dependencies installed)
2. When prompted: Frankfurt region, Yes to Postgres (Development), Yes to scale-to-zero, No to Redis
3. Verify at `https://your-app-name.fly.dev`
4. Verify DB with `/health` endpoint
5. Once confirmed working → move to Iteration 1
