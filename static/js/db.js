/**
 * IndexedDB wrapper for local-first learning platform
 *
 * Stores:
 * - config: Device settings (device_token, last_sync)
 * - cards: Cached cards from server
 * - progress: Local learning progress (never synced)
 * - notes: User notes per card (never synced)
 * - pending_responses: Responses waiting to sync
 * - sync_log: History of sync operations
 */

const DB_NAME = 'sociology-learning';
const DB_VERSION = 3;

let dbInstance = null;

// Session tracking - cards completed this session won't immediately reappear
// This resets on page refresh
const sessionCompletedCards = new Set();

/**
 * Open/create the database
 */
export async function openDB() {
    if (dbInstance) return dbInstance;

    return new Promise((resolve, reject) => {
        const request = indexedDB.open(DB_NAME, DB_VERSION);

        request.onerror = () => reject(request.error);

        request.onsuccess = () => {
            dbInstance = request.result;
            resolve(dbInstance);
        };

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // Config store - device settings
            if (!db.objectStoreNames.contains('config')) {
                db.createObjectStore('config', { keyPath: 'key' });
            }

            // Cards store - cached from server
            if (!db.objectStoreNames.contains('cards')) {
                const cardsStore = db.createObjectStore('cards', { keyPath: 'id' });
                cardsStore.createIndex('card_type', 'card_type', { unique: false });
                cardsStore.createIndex('visibility', 'visibility', { unique: false });
                cardsStore.createIndex('created_at', 'created_at', { unique: false });
            }

            // Progress store - local learning state
            if (!db.objectStoreNames.contains('progress')) {
                const progressStore = db.createObjectStore('progress', { keyPath: 'card_id' });
                progressStore.createIndex('status', 'status', { unique: false });
                progressStore.createIndex('scheduled_for', 'scheduled_for', { unique: false });
            }

            // Notes store - user notes per card
            if (!db.objectStoreNames.contains('notes')) {
                db.createObjectStore('notes', { keyPath: 'card_id' });
            }

            // Pending responses - waiting for sync
            if (!db.objectStoreNames.contains('pending_responses')) {
                const pendingStore = db.createObjectStore('pending_responses', {
                    keyPath: 'local_id',
                    autoIncrement: true
                });
                pendingStore.createIndex('card_id', 'card_id', { unique: false });
                pendingStore.createIndex('responded_at', 'responded_at', { unique: false });
            }

            // Sync log - history of syncs
            if (!db.objectStoreNames.contains('sync_log')) {
                const syncStore = db.createObjectStore('sync_log', {
                    keyPath: 'id',
                    autoIncrement: true
                });
                syncStore.createIndex('synced_at', 'synced_at', { unique: false });
            }

            // Drafts store - save work in progress (v2)
            if (!db.objectStoreNames.contains('drafts')) {
                db.createObjectStore('drafts', { keyPath: 'card_id' });
            }

            // Task pages store - cached task page content (v3)
            if (!db.objectStoreNames.contains('task_pages')) {
                const taskPagesStore = db.createObjectStore('task_pages', { keyPath: 'id' });
                taskPagesStore.createIndex('course_id', 'course_id', { unique: false });
                taskPagesStore.createIndex('updated_at', 'updated_at', { unique: false });
            }

            // Task page statuses - local status tracking (v3)
            if (!db.objectStoreNames.contains('task_page_statuses')) {
                const statusesStore = db.createObjectStore('task_page_statuses', { keyPath: 'task_page_id' });
                statusesStore.createIndex('status', 'status', { unique: false });
            }

            // Pending task updates - offline queue (v3)
            if (!db.objectStoreNames.contains('pending_task_updates')) {
                const pendingStore = db.createObjectStore('pending_task_updates', {
                    keyPath: 'id',
                    autoIncrement: true
                });
                pendingStore.createIndex('task_page_id', 'task_page_id', { unique: false });
            }
        };
    });
}

// =============================================================================
// CONFIG OPERATIONS
// =============================================================================

/**
 * Get a config value
 */
export async function getConfig(key) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('config', 'readonly');
        const store = tx.objectStore('config');
        const request = store.get(key);
        request.onsuccess = () => resolve(request.result?.value);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Set a config value
 */
export async function setConfig(key, value) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('config', 'readwrite');
        const store = tx.objectStore('config');
        const request = store.put({ key, value });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get or create device token
 */
export async function getOrCreateDeviceToken() {
    let token = await getConfig('device_token');
    if (!token) {
        token = crypto.randomUUID();
        await setConfig('device_token', token);
        console.log('Generated new device token:', token.substring(0, 8) + '...');
    }
    return token;
}

/**
 * Get last sync timestamp
 */
export async function getLastSync() {
    return await getConfig('last_sync');
}

/**
 * Set last sync timestamp
 */
export async function setLastSync(timestamp) {
    return await setConfig('last_sync', timestamp);
}

// =============================================================================
// COURSE SUBSCRIPTIONS
// =============================================================================

// Default courses - only sociology enabled by default
// ML courses require explicit opt-in
const DEFAULT_SUBSCRIBED_COURSES = ['sociology'];

/**
 * Get subscribed course slugs
 * Returns default if not set
 */
export async function getSubscribedCourses() {
    const stored = await getConfig('subscribed_courses');
    if (stored === undefined || stored === null) {
        return DEFAULT_SUBSCRIBED_COURSES;
    }
    return stored;
}

/**
 * Set subscribed course slugs
 */
export async function setSubscribedCourses(courseSlugs) {
    return await setConfig('subscribed_courses', courseSlugs);
}

/**
 * Check if a course is subscribed
 */
export async function isCourseSubscribed(courseSlug) {
    const subscribed = await getSubscribedCourses();
    return subscribed.includes(courseSlug);
}

/**
 * Toggle course subscription
 */
export async function toggleCourseSubscription(courseSlug) {
    const subscribed = await getSubscribedCourses();
    const index = subscribed.indexOf(courseSlug);
    if (index >= 0) {
        subscribed.splice(index, 1);
    } else {
        subscribed.push(courseSlug);
    }
    await setSubscribedCourses(subscribed);
    return subscribed;
}

// =============================================================================
// CARDS OPERATIONS
// =============================================================================

/**
 * Get all cached cards
 */
export async function getAllCards() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cards', 'readonly');
        const store = tx.objectStore('cards');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get a single card by ID
 */
export async function getCard(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cards', 'readonly');
        const store = tx.objectStore('cards');
        const request = store.get(id);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Save multiple cards (from sync)
 */
export async function saveCards(cards) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cards', 'readwrite');
        const store = tx.objectStore('cards');

        for (const card of cards) {
            store.put(card);
        }

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * Get card count
 */
export async function getCardCount() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cards', 'readonly');
        const store = tx.objectStore('cards');
        const request = store.count();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Clear all cards (used when changing subscriptions)
 */
export async function clearCards() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('cards', 'readwrite');
        const store = tx.objectStore('cards');
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

// =============================================================================
// PROGRESS OPERATIONS
// =============================================================================

/**
 * Progress status values:
 * - 'new': Never seen
 * - 'learning': In progress
 * - 'completed': Answered
 * - 'skipped': Temporarily skipped
 * - 'scheduled': Scheduled for future review
 */

/**
 * Get progress for a card
 */
export async function getProgress(cardId) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('progress', 'readonly');
        const store = tx.objectStore('progress');
        const request = store.get(cardId);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Update progress for a card
 */
export async function updateProgress(cardId, progressData) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('progress', 'readwrite');
        const store = tx.objectStore('progress');
        const request = store.put({
            card_id: cardId,
            updated_at: new Date().toISOString(),
            ...progressData
        });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Mark card as completed
 */
export async function markCompleted(cardId, scheduleType = 'never', scheduleDays = null) {
    const now = new Date();
    let scheduled_for = null;

    if (scheduleType === 'today') {
        scheduled_for = now.toISOString().split('T')[0]; // Today
    } else if (scheduleType === 'days' && scheduleDays) {
        const futureDate = new Date(now);
        futureDate.setDate(futureDate.getDate() + scheduleDays);
        scheduled_for = futureDate.toISOString().split('T')[0];
    }

    // Get existing progress to increment response_count
    const existing = await getProgress(cardId);
    const response_count = (existing?.response_count || 0) + 1;

    // Track in session to prevent immediate re-showing
    sessionCompletedCards.add(cardId);

    return updateProgress(cardId, {
        status: scheduled_for ? 'scheduled' : 'completed',
        completed_at: now.toISOString(),
        scheduled_for,
        response_count
    });
}

/**
 * Mark card as skipped
 */
export async function markSkipped(cardId) {
    return updateProgress(cardId, {
        status: 'skipped',
        skipped_at: new Date().toISOString()
    });
}

/**
 * Get all progress entries
 */
export async function getAllProgress() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('progress', 'readonly');
        const store = tx.objectStore('progress');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get cards due for review (scheduled_for <= today)
 */
export async function getDueCardIds() {
    const today = new Date().toISOString().split('T')[0];
    const allProgress = await getAllProgress();

    return allProgress
        .filter(p => p.status === 'scheduled' && p.scheduled_for && p.scheduled_for <= today)
        .map(p => p.card_id);
}

/**
 * Get next card to study
 * Priority order:
 * 1. New cards (never seen) - these always come first
 * 2. Due cards sorted by response_count ascending (least seen first)
 *    - Cards completed this session go to the end
 * 3. Skipped cards
 */
export async function getNextCard() {
    const cards = await getAllCards();
    const progressMap = new Map();

    const allProgress = await getAllProgress();
    for (const p of allProgress) {
        progressMap.set(p.card_id, p);
    }

    const today = new Date().toISOString().split('T')[0];

    // Categorize cards
    const due = [];
    const dueCompletedThisSession = [];
    const newCards = [];
    const skipped = [];

    for (const card of cards) {
        const progress = progressMap.get(card.id);

        if (!progress) {
            newCards.push(card);
        } else if (progress.status === 'scheduled' && progress.scheduled_for && progress.scheduled_for <= today) {
            // Separate cards completed this session from others
            if (sessionCompletedCards.has(card.id)) {
                dueCompletedThisSession.push({ card, response_count: progress.response_count || 0 });
            } else {
                due.push({ card, response_count: progress.response_count || 0 });
            }
        } else if (progress.status === 'skipped') {
            skipped.push(card);
        }
        // completed cards without schedule are not returned
    }

    // Sort due cards by response_count (ascending - least seen first)
    due.sort((a, b) => a.response_count - b.response_count);
    dueCompletedThisSession.sort((a, b) => a.response_count - b.response_count);

    // Return in priority order:
    // 1. New cards first (never seen)
    if (newCards.length > 0) return newCards[0];

    // 2. Due cards not completed this session (sorted by response_count)
    if (due.length > 0) return due[0].card;

    // 3. Skipped cards
    if (skipped.length > 0) return skipped[0];

    // 4. Due cards completed this session (only if nothing else available)
    if (dueCompletedThisSession.length > 0) return dueCompletedThisSession[0].card;

    return null;
}

/**
 * Clear session tracking (allows completed cards to appear again)
 * Call this if user wants to review cards they already did this session
 */
export function clearSessionTracking() {
    sessionCompletedCards.clear();
}

/**
 * Get the number of cards completed this session
 */
export function getSessionCompletedCount() {
    return sessionCompletedCards.size;
}

/**
 * Get learning stats
 */
export async function getStats() {
    const cards = await getAllCards();
    const progressMap = new Map();

    const allProgress = await getAllProgress();
    for (const p of allProgress) {
        progressMap.set(p.card_id, p);
    }

    const today = new Date().toISOString().split('T')[0];
    const todayStart = new Date(today).toISOString();

    let completedToday = 0;
    let totalCompleted = 0;
    let scheduled = 0;
    let newCards = 0;
    let skipped = 0;

    for (const card of cards) {
        const progress = progressMap.get(card.id);

        if (!progress) {
            newCards++;
        } else if (progress.status === 'completed' || progress.status === 'scheduled') {
            totalCompleted++;
            if (progress.completed_at && progress.completed_at >= todayStart) {
                completedToday++;
            }
            if (progress.status === 'scheduled') {
                scheduled++;
            }
        } else if (progress.status === 'skipped') {
            skipped++;
        }
    }

    return {
        total_cards: cards.length,
        completed_today: completedToday,
        total_completed: totalCompleted,
        scheduled: scheduled,
        new_cards: newCards,
        skipped: skipped,
        remaining: newCards + skipped + (await getDueCardIds()).length
    };
}

// =============================================================================
// NOTES OPERATIONS
// =============================================================================

/**
 * Get notes for a card
 */
export async function getNotes(cardId) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('notes', 'readonly');
        const store = tx.objectStore('notes');
        const request = store.get(cardId);
        request.onsuccess = () => resolve(request.result?.content || null);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Save notes for a card
 */
export async function saveNotes(cardId, content) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('notes', 'readwrite');
        const store = tx.objectStore('notes');

        if (content && content.trim()) {
            const request = store.put({
                card_id: cardId,
                content: content.trim(),
                updated_at: new Date().toISOString()
            });
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        } else {
            // Delete empty notes
            const request = store.delete(cardId);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        }
    });
}

// =============================================================================
// DRAFTS OPERATIONS
// =============================================================================

/**
 * Save a draft for a card
 * formData is an object with input values keyed by name or index
 */
export async function saveDraft(cardId, formData) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('drafts', 'readwrite');
        const store = tx.objectStore('drafts');
        const request = store.put({
            card_id: cardId,
            form_data: formData,
            saved_at: new Date().toISOString()
        });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get draft for a card
 */
export async function getDraft(cardId) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('drafts', 'readonly');
        const store = tx.objectStore('drafts');
        const request = store.get(cardId);
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Clear draft for a card (after submission)
 */
export async function clearDraft(cardId) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('drafts', 'readwrite');
        const store = tx.objectStore('drafts');
        const request = store.delete(cardId);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Check if a card has a draft
 */
export async function hasDraft(cardId) {
    const draft = await getDraft(cardId);
    return draft !== null;
}

// =============================================================================
// PENDING RESPONSES OPERATIONS
// =============================================================================

/**
 * Queue a response for later sync
 */
export async function queueResponse(cardId, responseContent, feedback = null) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_responses', 'readwrite');
        const store = tx.objectStore('pending_responses');
        const request = store.add({
            card_id: cardId,
            response_content: responseContent,
            responded_at: new Date().toISOString(),
            feedback: feedback // { rating, comment } or null
        });
        request.onsuccess = () => resolve(request.result); // Returns local_id
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get all pending responses
 */
export async function getPendingResponses() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_responses', 'readonly');
        const store = tx.objectStore('pending_responses');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get pending response count
 */
export async function getPendingCount() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_responses', 'readonly');
        const store = tx.objectStore('pending_responses');
        const request = store.count();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Clear pending responses (after successful sync)
 */
export async function clearPendingResponses() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_responses', 'readwrite');
        const store = tx.objectStore('pending_responses');
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

// =============================================================================
// SYNC LOG OPERATIONS
// =============================================================================

/**
 * Log a sync operation
 */
export async function logSync(responsesSent, cardsReceived) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('sync_log', 'readwrite');
        const store = tx.objectStore('sync_log');
        const request = store.add({
            synced_at: new Date().toISOString(),
            responses_sent: responsesSent,
            cards_received: cardsReceived
        });
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get recent sync logs
 */
export async function getRecentSyncs(limit = 10) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('sync_log', 'readonly');
        const store = tx.objectStore('sync_log');
        const index = store.index('synced_at');
        const request = index.openCursor(null, 'prev');

        const results = [];
        request.onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor && results.length < limit) {
                results.push(cursor.value);
                cursor.continue();
            } else {
                resolve(results);
            }
        };
        request.onerror = () => reject(request.error);
    });
}

// =============================================================================
// TASK PAGES OPERATIONS
// =============================================================================

/**
 * Get all cached task pages
 */
export async function getAllTaskPages() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_pages', 'readonly');
        const store = tx.objectStore('task_pages');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get a single task page by ID
 */
export async function getTaskPage(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_pages', 'readonly');
        const store = tx.objectStore('task_pages');
        const request = store.get(id);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Save a task page (from server)
 */
export async function saveTaskPage(taskPage) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_pages', 'readwrite');
        const store = tx.objectStore('task_pages');
        const request = store.put(taskPage);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Save multiple task pages (from sync)
 */
export async function saveTaskPages(taskPages) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_pages', 'readwrite');
        const store = tx.objectStore('task_pages');

        for (const page of taskPages) {
            store.put(page);
        }

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

/**
 * Get task page count
 */
export async function getTaskPageCount() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_pages', 'readonly');
        const store = tx.objectStore('task_pages');
        const request = store.count();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// =============================================================================
// TASK PAGE STATUS OPERATIONS
// =============================================================================

/**
 * Get status for a task page
 */
export async function getTaskPageStatus(taskPageId) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_page_statuses', 'readonly');
        const store = tx.objectStore('task_page_statuses');
        const request = store.get(taskPageId);
        request.onsuccess = () => resolve(request.result || { task_page_id: taskPageId, status: 'not_started' });
        request.onerror = () => reject(request.error);
    });
}

/**
 * Update status for a task page locally
 */
export async function updateTaskPageStatus(taskPageId, status, notes = null) {
    const db = await openDB();
    const now = new Date().toISOString();

    // Get existing status
    const existing = await getTaskPageStatus(taskPageId);

    const statusData = {
        task_page_id: taskPageId,
        status,
        updated_at: now,
        started_at: existing.started_at,
        completed_at: existing.completed_at,
        notes: notes !== null ? notes : existing.notes
    };

    // Set timestamps based on status transitions
    if (['draft', 'in_progress', 'completed'].includes(status) && !statusData.started_at) {
        statusData.started_at = now;
    }
    if (status === 'completed' && !statusData.completed_at) {
        statusData.completed_at = now;
    }

    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_page_statuses', 'readwrite');
        const store = tx.objectStore('task_page_statuses');
        const request = store.put(statusData);
        request.onsuccess = () => resolve(statusData);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get all task page statuses
 */
export async function getAllTaskPageStatuses() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_page_statuses', 'readonly');
        const store = tx.objectStore('task_page_statuses');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Bulk update statuses (from server sync)
 */
export async function saveTaskPageStatuses(statuses) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('task_page_statuses', 'readwrite');
        const store = tx.objectStore('task_page_statuses');

        for (const status of statuses) {
            store.put(status);
        }

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

// =============================================================================
// PENDING TASK UPDATES (OFFLINE QUEUE)
// =============================================================================

/**
 * Queue a task page status update for sync
 */
export async function queueTaskUpdate(taskPageId, status, notes = null) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_task_updates', 'readwrite');
        const store = tx.objectStore('pending_task_updates');
        const request = store.add({
            task_page_id: taskPageId,
            status,
            notes,
            queued_at: new Date().toISOString()
        });
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get all pending task updates
 */
export async function getPendingTaskUpdates() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_task_updates', 'readonly');
        const store = tx.objectStore('pending_task_updates');
        const request = store.getAll();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

/**
 * Remove a pending task update (after successful sync)
 */
export async function removePendingTaskUpdate(id) {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_task_updates', 'readwrite');
        const store = tx.objectStore('pending_task_updates');
        const request = store.delete(id);
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Clear all pending task updates
 */
export async function clearPendingTaskUpdates() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_task_updates', 'readwrite');
        const store = tx.objectStore('pending_task_updates');
        const request = store.clear();
        request.onsuccess = () => resolve();
        request.onerror = () => reject(request.error);
    });
}

/**
 * Get pending task update count
 */
export async function getPendingTaskUpdateCount() {
    const db = await openDB();
    return new Promise((resolve, reject) => {
        const tx = db.transaction('pending_task_updates', 'readonly');
        const store = tx.objectStore('pending_task_updates');
        const request = store.count();
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

// =============================================================================
// INITIALIZATION
// =============================================================================

/**
 * Initialize database and return device token
 */
export async function initDB() {
    await openDB();
    const deviceToken = await getOrCreateDeviceToken();
    return { deviceToken };
}
