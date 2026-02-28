# Manual Test Plans for Sociology Learning PWA

These tests are designed to be executed by Claude Chrome Extension or a human tester.
Each test includes setup links that prepare the test state.

**Base URL:** `https://sociology-learning-pwa-staging.fly.dev`

---

## Test 1: Fresh Start - Complete Learning Flow

**Purpose:** Verify the basic learning flow from a fresh state.

### Prerequisites
Clear browser site data before starting, or use the setup link below.

### Setup
1. Click: [Reset Client State](/api/test/reset-client) - This returns instructions to clear IndexedDB

### Steps

1. **Load the app**
   - Navigate to `/`
   - **Verify:** App loads without console errors
   - **Verify:** A card is displayed (Sozialisation card or similar)
   - **Verify:** Stats show `0/X` completed today

2. **Check IndexedDB initialization**
   - Open DevTools → Application → IndexedDB → `sociology-learning`
   - **Verify:** `config` store exists with `device_token` entry
   - **Verify:** `cards` store contains at least 1 card
   - **Verify:** `progress` store is empty
   - **Verify:** `pending_responses` store is empty

3. **Submit a response**
   - Type an answer in the textarea (at least 10 characters)
   - Click "Antwort senden"
   - **Verify:** Success message appears
   - **Verify:** Scheduling options appear (Heute nochmal / In X Tagen / Nicht wiederholen)

4. **Check pending response in IndexedDB**
   - Refresh IndexedDB view
   - **Verify:** `pending_responses` store now has 1 entry
   - **Verify:** Entry contains `card_id`, `response_content`, `responded_at`

5. **Select a schedule and continue**
   - Select "Nicht wiederholen"
   - Click "Weiter"
   - **Verify:** Card advances (either next card or "no more cards" message)
   - **Verify:** `progress` store now has 1 entry with status `completed`

6. **Sync with server**
   - Open DevTools → Network tab (clear existing entries)
   - Click the sync button (cloud icon in header)
   - **Verify:** POST request to `/api/sync` appears in Network tab

   **Verify Request Payload (click request → Payload tab):**
   ```json
   {
     "device_token": "<uuid string>",
     "responses": [
       {
         "card_id": <number>,
         "response_content": { "answer": "<your typed answer>" },
         "responded_at": "<ISO timestamp>",
         "feedback": null
       }
     ],
     "last_sync": null
   }
   ```

   **Verify Response (click request → Response tab):**
   ```json
   {
     "success": true,
     "responses_received": 1,
     "new_cards": [...],
     "stats": {
       "total_responses": <number>,
       "pending_evaluations": <number>,
       "cards_available": <number>
     }
   }
   ```

   - **Verify:** `pending_responses` store is now empty after sync

### Expected Result
Response is stored locally, synced to server, and local queue is cleared.

---

## Test 2: Offline Mode - Queue and Sync

**Purpose:** Verify responses are queued when offline and synced when back online.

### Setup
1. Click: [Seed Multiple Cards](/api/test/seed-cards?count=3) - Adds 3 test cards
2. Clear site data and reload the app

### Steps

1. **Go offline**
   - Open DevTools → Network → Check "Offline"
   - **Verify:** Offline indicator appears at bottom of page
   - **Verify:** Sync button shows offline state

2. **Submit responses while offline**
   - Answer the first card, select schedule, continue
   - Answer the second card, select schedule, continue
   - **Verify:** Both submissions succeed (stored locally)
   - **Verify:** `pending_responses` store has 2 entries

3. **Attempt sync while offline**
   - Click sync button
   - **Verify:** Sync fails gracefully (no crash)
   - **Verify:** Pending responses remain in IndexedDB

4. **Go back online**
   - Uncheck "Offline" in DevTools
   - **Verify:** Online indicator updates
   - **Verify:** Sync button shows "2 pending"

5. **Sync pending responses**
   - Open DevTools → Network tab (clear existing entries)
   - Click sync button
   - **Verify:** POST request to `/api/sync` appears

   **Verify Request Payload contains both responses:**
   ```json
   {
     "device_token": "<uuid>",
     "responses": [
       { "card_id": 1, "response_content": {...}, ... },
       { "card_id": 2, "response_content": {...}, ... }
     ],
     "last_sync": null
   }
   ```

   **Verify Response:**
   ```json
   {
     "success": true,
     "responses_received": 2,
     "new_cards": [...],
     "stats": {...}
   }
   ```

   - **Verify:** `pending_responses` store is now empty

### Expected Result
Responses queue locally when offline and sync successfully when online.

---

## Test 3: Notes Persistence

**Purpose:** Verify notes are saved locally and persist across sessions.

### Setup
1. Clear site data and reload the app

### Steps

1. **Open notes drawer**
   - Click the notes icon on the current card
   - **Verify:** Notes drawer opens (empty)

2. **Add notes**
   - Click edit/add button
   - Type: "This is a test note for card 1"
   - Click save
   - **Verify:** Notes display in rendered markdown
   - **Verify:** `notes` store in IndexedDB has 1 entry

3. **Close and reopen notes**
   - Close the notes drawer
   - Reopen it
   - **Verify:** Notes are still visible

4. **Reload the page**
   - Hard refresh the page (Cmd+Shift+R)
   - Open notes drawer
   - **Verify:** Notes persist after reload

5. **Edit notes**
   - Click edit button
   - Add more text: "Updated with more info"
   - Save
   - **Verify:** Notes update correctly

### Expected Result
Notes are stored in IndexedDB and persist across page reloads.

---

## Test Setup API Endpoints

These endpoints are **staging-only** and will return 404 on production.

### GET /api/test/reset-client
Returns instructions for clearing client-side state.

### GET /api/test/seed-cards?count=N
Adds N test cards to the database for testing.

**Response:**
```json
{
  "success": true,
  "cards_added": 3,
  "message": "Added 3 test cards"
}
```

### GET /api/test/clear-responses?device_token=XXX
Clears all responses for a specific device token.

**Response:**
```json
{
  "success": true,
  "responses_deleted": 5
}
```

### GET /api/test/db-state?device_token=XXX
Returns current database state for debugging.

**Response:**
```json
{
  "cards_count": 10,
  "responses_count": 5,
  "device_responses": 2
}
```

---

## Notes for Claude Extension

When executing these tests:

1. **Clear site data** before each test using DevTools → Application → Clear site data
2. **Monitor IndexedDB** using DevTools → Application → IndexedDB
3. **Check Network tab** for API requests during sync
4. **Check Console** for any JavaScript errors
5. **Use the setup links** to prepare test state before running steps

The setup endpoints use GET requests so they can be clicked as links or fetched easily.
