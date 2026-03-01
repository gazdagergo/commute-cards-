# Bug Re-test Report: Letzte Synchronisation UI Label

**Date:** 2026-03-02
**Environment:** https://sociology-learning-pwa-staging.fly.dev
**Tester:** Claude (automated via Chrome Extension)
**Related Test:** Test 1 — Step 7 (Sync with Server)
**Overall Result:** ❌ FAILED — Bug not fixed

---

## Issue Description

After a successful sync, the "Letzte Synchronisation" label in the UI continues to display **"Never synced"** instead of the actual last sync timestamp.

---

## Re-test Steps

### 1. Hard reload app to pick up latest deployed changes
- Hard reloaded the app (Cmd+Shift+R)
- App loaded correctly

### 2. Submit a response and advance to sync screen
- Submitted a valid answer to the Sozialisation card
- Selected "Nicht wiederholen"
- Clicked "Weiter"
- Reached "Alles erledigt!" screen with "Synchronisieren" button visible
- Label before sync: **"Letzte Synchronisation: Never synced"** (expected)

### 3. Clicked "Synchronisieren" and observed result
- POST `/api/sync` → **HTTP 200 OK** ✅
- `sync_log` in IndexedDB correctly updated:

```json
[{
  "id": 1,
  "synced_at": "2026-03-02T19:17:47.089Z",
  "responses_sent": 1,
  "cards_received": 1
}]
```

- Label after sync: ❌ **Still shows "Letzte Synchronisation: Never synced"**

---

## Root Cause Analysis

Inspected the Alpine.js component state after sync:

```json
{
  "syncState": {
    "isOnline": true,
    "isSyncing": false,
    "lastSyncTime": "2026-03-02T19:17:47.088Z",
    "pendingCount": 0,
    "error": null
  },
  "lastSyncText": "Just now"
}
```

| Layer | Status | Value |
|---|---|---|
| `syncState.lastSyncTime` (Alpine data) | ✅ Correct | `"2026-03-02T19:17:47.088Z"` |
| `getLastSyncText()` (Alpine function) | ✅ Correct | `"Just now"` |
| DOM label (`x-text` binding) | ❌ Not updated | `"Never synced"` |

**Conclusion:** The Alpine.js `x-text` binding for `'Letzte Synchronisation: ' + getLastSyncText()` is not re-rendering after sync completes. The data is correct but Alpine's reactivity is not triggered. Most likely `syncState.lastSyncTime` is being set asynchronously (inside a Promise or IDB callback) outside of Alpine's reactive context, so the DOM binding does not detect the change.

---

## Expected vs Actual

| | Expected | Actual |
|---|---|---|
| Label after sync | "Letzte Synchronisation: Just now" (or formatted timestamp) | "Letzte Synchronisation: Never synced" |

---

## Recommendation

Ensure `syncState.lastSyncTime` is set within Alpine's reactive context after sync completes. For example, using `Alpine.store()` mutation or wrapping the assignment in a way Alpine can track the change (e.g. directly mutating a reactive property within an Alpine method rather than inside an async IDB callback).
