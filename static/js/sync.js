/**
 * Sync module for local-first learning platform
 *
 * Handles:
 * - Initial card fetch
 * - Manual sync (upload responses, download new cards)
 * - Online/offline detection
 */

import {
    getOrCreateDeviceToken,
    getLastSync,
    setLastSync,
    saveCards,
    getPendingResponses,
    clearPendingResponses,
    logSync,
    getCardCount,
    getPendingCount
} from './db.js';

const API_BASE = '';  // Same origin

/**
 * Sync state for UI binding
 */
export const syncState = {
    isOnline: navigator.onLine,
    isSyncing: false,
    lastSyncTime: null,
    pendingCount: 0,
    error: null
};

/**
 * Initialize sync module
 */
export async function initSync() {
    // Set up online/offline listeners
    window.addEventListener('online', () => {
        syncState.isOnline = true;
        console.log('Network: online');
    });

    window.addEventListener('offline', () => {
        syncState.isOnline = false;
        console.log('Network: offline');
    });

    // Load initial state
    syncState.lastSyncTime = await getLastSync();
    syncState.pendingCount = await getPendingCount();

    return syncState;
}

/**
 * Update pending count (call after queueing a response)
 */
export async function updatePendingCount() {
    syncState.pendingCount = await getPendingCount();
    return syncState.pendingCount;
}

/**
 * Fetch initial cards (first load or cache refresh)
 */
export async function fetchInitialCards() {
    if (!syncState.isOnline) {
        console.log('Offline - using cached cards');
        return { success: false, reason: 'offline' };
    }

    try {
        const deviceToken = await getOrCreateDeviceToken();
        const response = await fetch(`${API_BASE}/api/cards?device_token=${encodeURIComponent(deviceToken)}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        const cards = data.cards || [];

        if (cards.length > 0) {
            await saveCards(cards);
            console.log(`Cached ${cards.length} cards`);
        }

        return { success: true, count: cards.length };
    } catch (error) {
        console.error('Failed to fetch cards:', error);
        syncState.error = error.message;
        return { success: false, reason: error.message };
    }
}

/**
 * Perform full sync:
 * 1. Upload pending responses
 * 2. Download new cards since last sync
 * 3. Update local state
 */
export async function performSync() {
    if (syncState.isSyncing) {
        console.log('Sync already in progress');
        return { success: false, reason: 'already_syncing' };
    }

    if (!syncState.isOnline) {
        console.log('Cannot sync - offline');
        return { success: false, reason: 'offline' };
    }

    syncState.isSyncing = true;
    syncState.error = null;

    try {
        const deviceToken = await getOrCreateDeviceToken();
        const lastSync = await getLastSync();
        const pendingResponses = await getPendingResponses();

        // Build sync request
        const syncRequest = {
            device_token: deviceToken,
            responses: pendingResponses.map(r => ({
                card_id: r.card_id,
                response_content: r.response_content,
                responded_at: r.responded_at,
                feedback: r.feedback
            })),
            last_sync: lastSync
        };

        console.log(`Syncing: ${pendingResponses.length} responses to upload`);

        const response = await fetch(`${API_BASE}/api/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(syncRequest)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }

        const result = await response.json();

        // Save new cards
        if (result.new_cards && result.new_cards.length > 0) {
            await saveCards(result.new_cards);
            console.log(`Received ${result.new_cards.length} new cards`);
        }

        // Clear pending responses (they've been sent)
        if (result.responses_received > 0) {
            await clearPendingResponses();
            console.log(`Cleared ${result.responses_received} pending responses`);
        }

        // Update sync timestamp
        const now = new Date().toISOString();
        await setLastSync(now);
        syncState.lastSyncTime = now;
        syncState.pendingCount = 0;

        // Log the sync
        await logSync(result.responses_received || 0, result.new_cards?.length || 0);

        return {
            success: true,
            responses_sent: result.responses_received || 0,
            cards_received: result.new_cards?.length || 0,
            stats: result.stats
        };

    } catch (error) {
        console.error('Sync failed:', error);
        syncState.error = error.message;
        return { success: false, reason: error.message };
    } finally {
        syncState.isSyncing = false;
    }
}

/**
 * Check if we have any cached cards
 */
export async function hasCachedCards() {
    const count = await getCardCount();
    return count > 0;
}

/**
 * Get sync status for UI display
 */
export function getSyncStatus() {
    if (!syncState.isOnline) {
        return { icon: 'offline', text: 'Offline', class: 'text-gray-500' };
    }

    if (syncState.isSyncing) {
        return { icon: 'syncing', text: 'Syncing...', class: 'text-indigo-600' };
    }

    if (syncState.pendingCount > 0) {
        return {
            icon: 'pending',
            text: `${syncState.pendingCount} pending`,
            class: 'text-amber-600'
        };
    }

    return { icon: 'synced', text: 'Synced', class: 'text-green-600' };
}

/**
 * Format last sync time for display
 */
export function formatLastSync() {
    if (!syncState.lastSyncTime) {
        return 'Never synced';
    }

    const syncDate = new Date(syncState.lastSyncTime);
    const now = new Date();
    const diffMs = now - syncDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return syncDate.toLocaleDateString('de-DE');
}