# Media Player Implementation Plan

## Overview

Add a 4th "Media" tab to the commute-cards app with synchronized transcript playback for audio and video content.

## Architecture Summary

### Current State
- **App:** Flask backend + Alpine.js SPA in single HTML file
- **Tabs:** 3 tabs (Karten, Feed, Aufgaben)
- **Navigation:** Alpine.js `activeTab` with classList manipulation
- **Storage:** PostgreSQL server + IndexedDB client (local-first sync)

### Reference Implementation
- **Video player with transcript:** `video-player/player.html`
- **Transcript data format:** `[{text: string, timestamp: number}]`
- **Existing transcripts:**
  - `materials/sociology/transcripts/dorett-fucke-audio-timestamps.json` (62 lines)
  - `video-player/circular-cities-timestamps.json`

---

## Files to Modify

### 1. `commute-cards/static/js/db.js`

Add IndexedDB stores (bump version 3 → 4):

```javascript
// New stores in upgrade handler
if (oldVersion < 4) {
    // Media items cache
    const mediaStore = db.createObjectStore('media_items', { keyPath: 'id' });
    mediaStore.createIndex('course_id', 'course_id');
    mediaStore.createIndex('media_type', 'media_type');

    // Transcripts cache
    const transcriptStore = db.createObjectStore('transcripts', { keyPath: 'id' });
    transcriptStore.createIndex('media_id', 'media_id');

    // Local playback progress (never synced)
    db.createObjectStore('media_progress', { keyPath: 'media_id' });
}
```

New functions to add:
- `getAllMediaItems()` - Get all cached media items
- `getMediaItem(id)` - Get single media item
- `saveMediaItems(items)` - Cache media items from server
- `getTranscript(id)` - Get cached transcript
- `saveTranscript(transcript)` - Cache transcript
- `getMediaProgress(mediaId)` - Get playback position
- `saveMediaProgress(mediaId, position, completed)` - Save progress

---

### 2. `commute-cards/static/js/app.js`

Add new `mediaApp()` Alpine.js component:

```javascript
export function mediaApp() {
    return {
        // List state
        mediaItems: [],
        loading: true,
        error: null,

        // Playback state
        currentMedia: null,
        isPlaying: false,
        currentTime: 0,
        duration: 0,

        // Transcript state
        transcript: null,
        transcriptLoading: false,
        activeLineIndex: 0,
        userIsScrolling: false,
        scrollTimeout: null,

        // View state
        currentView: 'list',  // 'list' | 'player'

        async init() {
            await this.loadMediaItems();
        },

        // Transcript sync logic (from video-player/player.html)
        onTimeUpdate(event) {
            this.currentTime = event.target.currentTime;
            this.updateActiveTranscriptLine();
            this.debouncedSaveProgress();
        },

        updateActiveTranscriptLine() {
            if (!this.transcript?.lines) return;

            let activeIndex = 0;
            for (let i = 0; i < this.transcript.lines.length; i++) {
                if (this.transcript.lines[i].timestamp <= this.currentTime) {
                    activeIndex = i;
                } else {
                    break;
                }
            }

            this.activeLineIndex = activeIndex;

            // Auto-scroll if not manually scrolling
            if (!this.userIsScrolling) {
                this.$refs.transcriptPanel?.children[activeIndex]
                    ?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        },

        seekToLine(index) {
            const timestamp = this.transcript.lines[index]?.timestamp;
            if (timestamp != null && this.$refs.mediaPlayer) {
                this.$refs.mediaPlayer.currentTime = timestamp;
                this.$refs.mediaPlayer.play();
            }
        },

        onTranscriptScroll() {
            this.userIsScrolling = true;
            clearTimeout(this.scrollTimeout);
            this.scrollTimeout = setTimeout(() => {
                this.userIsScrolling = false;
            }, 3000);
        },

        // ... other methods
    };
}
```

Register globally:
```javascript
window.mediaApp = mediaApp;
```

---

### 3. `commute-cards/templates/index.html`

**Add Media section** (insert before bottom navigation, ~line 799):

```html
<!-- Media Section -->
<div id="media-app" x-data="mediaApp()" x-init="init()" x-cloak class="hidden max-w-lg mx-auto">
    <!-- List View -->
    <div x-show="currentView === 'list'">
        <!-- Header -->
        <!-- Media item cards -->
    </div>

    <!-- Player View -->
    <div x-show="currentView === 'player'">
        <!-- Back header -->
        <!-- Video/Audio player -->
        <!-- Progress bar -->
        <!-- Transcript panel -->
    </div>
</div>
```

**Update bottom navigation** (lines 799-831):

Add 4th tab button for "Medien":
```html
<!-- Media tab (NEW) -->
<button @click="activeTab = 'media';
               document.querySelector('[x-data*=learningApp]').classList.add('hidden');
               document.getElementById('feed-app').classList.add('hidden');
               document.getElementById('task-pages-app').classList.add('hidden');
               document.getElementById('media-app').classList.remove('hidden')"
        class="flex-1 py-3 flex flex-col items-center gap-1 transition-colors"
        :class="activeTab === 'media' ? 'text-indigo-600' : 'text-gray-400'">
    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
    <span class="text-xs font-medium">Medien</span>
</button>
```

Update existing tab click handlers to also hide `media-app`.

---

### 4. `commute-cards/app.py`

**Add database tables:**

```sql
CREATE TABLE IF NOT EXISTS media_items (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    media_type VARCHAR(20) NOT NULL,  -- 'audio' or 'video'
    media_url TEXT NOT NULL,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    duration_formatted VARCHAR(20),
    transcript_id VARCHAR(64),
    course_id INTEGER,
    learning_unit VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS media_transcripts (
    id VARCHAR(64) PRIMARY KEY,
    media_id VARCHAR(64) REFERENCES media_items(id) ON DELETE CASCADE,
    lines JSONB NOT NULL,  -- Array of {text, timestamp}
    language VARCHAR(10) DEFAULT 'de',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Add API endpoints:**

```python
@app.route("/api/media")
def get_media_items():
    """List all media items (optionally filtered by course)"""
    # Return media items from database

@app.route("/api/media/<media_id>/transcript")
def get_media_transcript(media_id):
    """Get transcript for a media item"""
    # Return transcript JSON
```

---

## Data Structures

### Media Item
```json
{
    "id": "dorit-funke-interview",
    "title": "Interview mit Prof. Dorit Funke",
    "description": "Mikrosoziologie und Forschungsfeld",
    "media_type": "audio",
    "media_url": "https://firebasestorage.googleapis.com/...",
    "duration_seconds": 332,
    "duration_formatted": "5:32",
    "transcript_id": "dorit-funke-interview",
    "learning_unit": "LE_IV"
}
```

### Transcript (existing format)
```json
{
    "id": "dorit-funke-interview",
    "media_id": "dorit-funke-interview",
    "lines": [
        {"text": "Hallo, liebe Studierende!", "timestamp": null},
        {"text": "Ich sitze ja heute mit Frau Professorin Dorit Funke.", "timestamp": 3.914829},
        // ...
    ],
    "language": "de"
}
```

### Playback Progress (local only)
```json
{
    "media_id": "dorit-funke-interview",
    "position_seconds": 45.2,
    "last_played_at": "2026-05-10T14:30:00Z",
    "completed": false
}
```

---

## UI Layout (Mobile-First)

### List View
```
┌─────────────────────────────┐
│ Header: "Medien"      [↻]  │
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │ 🎵  Title              >│ │
│ │     Description          │ │
│ │     5:32  [LE_IV]        │ │
│ └─────────────────────────┘ │
│ ┌─────────────────────────┐ │
│ │ 🎬  Title              >│ │
│ │     ...                  │ │
│ └─────────────────────────┘ │
└─────────────────────────────┘
│ [Karten] [Feed] [Medien] [Aufgaben] │
```

### Player View
```
┌─────────────────────────────┐
│ ← Title                     │
├─────────────────────────────┤
│                             │
│    [Video/Audio Player]     │
│                             │
├─────────────────────────────┤
│ 1:23 ──────────────── 5:32  │
├─────────────────────────────┤
│ ┌─────────────────────────┐ │
│ │ 0:03 Previous line      │ │
│ └─────────────────────────┘ │
│ ┌═════════════════════════┐ │
│ ║ 0:08 Active line (blue) ║ │
│ └═════════════════════════┘ │
│ ┌─────────────────────────┐ │
│ │ 0:13 Next line          │ │
│ └─────────────────────────┘ │
│         (scrollable)        │
└─────────────────────────────┘
```

---

## Implementation Order

1. **Database layer** (`db.js`) - Add IndexedDB stores and functions
2. **Backend API** (`app.py`) - Add tables and endpoints
3. **Alpine component** (`app.js`) - Add `mediaApp()` with transcript sync
4. **HTML template** (`index.html`) - Add section and update navigation
5. **Seed data** - Insert initial media items (Dorit Funke audio, Circular Cities video)

---

## Initial Media Content

| ID | Title | Type | Source | Transcript |
|----|-------|------|--------|------------|
| `dorit-funke-interview` | Interview mit Prof. Dorit Funke | audio | Firebase (to upload) | `dorett-fucke-audio-timestamps.json` |
| `circular-cities-video` | Circular Cities NRW | video | Firebase (existing) | `circular-cities-timestamps.json` |

---

## Verification Checklist

- [ ] Open app, verify 4th "Medien" tab appears in bottom nav
- [ ] Tap Media tab - list of available media displays
- [ ] Tap media item - player view opens with transcript
- [ ] Play media - transcript highlights current sentence
- [ ] Tap transcript line - media seeks to that timestamp
- [ ] Scroll transcript manually - auto-scroll pauses for 3 seconds
- [ ] Leave player and return - playback position restored
- [ ] Works offline with cached data