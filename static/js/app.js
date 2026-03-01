/**
 * Main application module for local-first learning platform
 *
 * This module:
 * - Initializes the database and sync
 * - Provides Alpine.js components
 * - Manages the learning flow using local data
 */

import * as db from './db.js';
import * as sync from './sync.js';

// Make db and sync available globally for debugging
window.db = db;
window.sync = sync;

/**
 * Initialize the app
 * Called before Alpine.js starts
 */
export async function initApp() {
    console.log('Initializing local-first learning app...');

    try {
        // Initialize database
        const { deviceToken } = await db.initDB();
        console.log('Device token:', deviceToken.substring(0, 8) + '...');

        // Initialize sync
        await sync.initSync();

        // Check if we have cached cards
        const hasCached = await sync.hasCachedCards();

        if (!hasCached && sync.syncState.isOnline) {
            // First load - fetch cards from server
            console.log('No cached cards - fetching from server...');
            const result = await sync.fetchInitialCards();
            if (result.success) {
                console.log(`Initial fetch: ${result.count} cards cached`);
            }
        } else if (hasCached) {
            const count = await db.getCardCount();
            console.log(`Using ${count} cached cards`);
        }

        return { success: true, deviceToken };
    } catch (error) {
        console.error('Failed to initialize app:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Global cardResponse component for card HTML snippets
 * Cards use this to submit responses
 */
export function cardResponse() {
    return {
        submitting: false,
        submitted: false,
        error: null,

        async submitResponse(data) {
            this.submitting = true;
            this.error = null;

            try {
                // Get the card ID from the parent learningApp
                const appEl = document.querySelector('[x-data*="learningApp"]');
                const app = Alpine.$data(appEl);
                const cardId = app.currentCard?.id;

                if (!cardId) {
                    throw new Error('Keine Karte geladen');
                }

                // Queue response locally (don't send to server yet)
                const localId = await db.queueResponse(cardId, data);
                console.log('Response queued locally:', localId);

                // Update pending count
                await sync.updatePendingCount();

                this.submitted = true;

                // Notify parent app
                app.onCardSubmitted('Lokal gespeichert', localId);

            } catch (e) {
                console.error('Failed to queue response:', e);
                this.error = e.message;
            } finally {
                this.submitting = false;
            }
        }
    };
}

/**
 * Main learning app component
 */
export function learningApp() {
    return {
        // App state
        initialized: false,
        currentCard: null,
        loading: true,
        submitting: false,
        successMessage: '',

        // Stats (initialized with defaults to prevent null errors during render)
        stats: {
            total_cards: 0,
            completed_today: 0,
            total_completed: 0,
            scheduled: 0,
            new_cards: 0,
            skipped: 0,
            remaining: 0
        },

        // Sync state (bound to sync module)
        syncState: sync.syncState,

        // Feedback state
        showFeedback: false,
        currentLocalId: null,
        feedbackRating: 0,
        feedbackComment: '',
        submittingFeedback: false,

        // Scheduling state
        scheduleType: null,
        scheduleDays: 3,

        // Notes state
        notesDrawerOpen: false,
        notesEditMode: false,
        notesEditText: '',
        notesSaving: false,

        /**
         * Initialize on mount
         */
        async init() {
            await initApp();
            this.initialized = true;
            await this.loadNextCard();
        },

        /**
         * Load the next card from local database
         */
        async loadNextCard() {
            this.loading = true;
            this.showFeedback = false;
            this.resetFeedback();
            this.closeNotesDrawer();

            try {
                // Get next card from local database
                const card = await db.getNextCard();

                if (card) {
                    // Load notes for this card
                    const notes = await db.getNotes(card.id);
                    this.currentCard = { ...card, notes };
                } else {
                    this.currentCard = null;
                }

                // Update stats
                this.stats = await db.getStats();

            } catch (e) {
                console.error('Failed to load card:', e);
                this.currentCard = null;
            } finally {
                this.loading = false;
            }
        },

        /**
         * Reset feedback form
         */
        resetFeedback() {
            this.feedbackRating = 0;
            this.feedbackComment = '';
            this.currentLocalId = null;
            this.scheduleType = null;
            this.scheduleDays = 3;
        },

        /**
         * Called when a card response is submitted
         */
        onCardSubmitted(message, localId) {
            this.successMessage = message || 'Gespeichert';
            this.currentLocalId = localId;
            this.showFeedback = true;
        },

        /**
         * Submit schedule and optional feedback
         */
        async submitScheduleAndFeedback() {
            if (!this.scheduleType || this.submittingFeedback) return;

            this.submittingFeedback = true;

            try {
                // Update local progress with schedule
                await db.markCompleted(
                    this.currentCard.id,
                    this.scheduleType,
                    this.scheduleType === 'days' ? this.scheduleDays : null
                );

                // If feedback provided, update the pending response
                // (feedback will be sent with the response during sync)
                if (this.feedbackRating > 0 && this.currentLocalId) {
                    // Note: In a real implementation, we'd update the pending response
                    // For now, feedback is included when queueResponse is called
                    console.log('Feedback:', this.feedbackRating, this.feedbackComment);
                }

            } catch (e) {
                console.error('Failed to save schedule:', e);
            } finally {
                this.submittingFeedback = false;
                this.loadNextCard();
            }
        },

        /**
         * Skip the current card
         */
        async skipCard() {
            if (!this.currentCard || this.submitting) return;

            this.submitting = true;

            try {
                await db.markSkipped(this.currentCard.id);
                await this.loadNextCard();
            } catch (e) {
                console.error('Failed to skip card:', e);
            } finally {
                this.submitting = false;
            }
        },

        /**
         * Manual sync button handler
         */
        async doSync() {
            if (this.syncState.isSyncing) return;

            const result = await sync.performSync();

            // Force Alpine to detect syncState changes by creating new object reference
            this.syncState = { ...sync.syncState };

            if (result.success) {
                console.log(`Sync complete: sent ${result.responses_sent}, received ${result.cards_received}`);
                // Refresh stats and potentially the current card
                this.stats = await db.getStats();

                // If we received new cards, notify the user
                if (result.cards_received > 0) {
                    // Could show a toast notification here
                    console.log(`${result.cards_received} new cards available`);
                }
            }

            return result;
        },

        /**
         * Get sync status for display
         */
        getSyncStatus() {
            return sync.getSyncStatus();
        },

        /**
         * Get formatted last sync time
         * Note: Uses this.syncState directly for Alpine reactivity
         */
        getLastSyncText() {
            const lastSyncTime = this.syncState.lastSyncTime;
            if (!lastSyncTime) {
                return 'Never synced';
            }

            const syncDate = new Date(lastSyncTime);
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
        },

        // =================================================================
        // Notes methods
        // =================================================================

        openNotesDrawer() {
            this.notesDrawerOpen = true;
            this.notesEditMode = false;
        },

        closeNotesDrawer() {
            this.notesDrawerOpen = false;
            this.notesEditMode = false;
            this.notesEditText = '';
        },

        enterNotesEditMode() {
            this.notesEditText = this.currentCard?.notes || '';
            this.notesEditMode = true;
        },

        cancelNotesEdit() {
            this.notesEditMode = false;
            this.notesEditText = '';
        },

        async saveNotes() {
            if (!this.currentCard || this.notesSaving) return;

            this.notesSaving = true;

            try {
                await db.saveNotes(this.currentCard.id, this.notesEditText);
                // Update local state
                this.currentCard.notes = this.notesEditText.trim() || null;
                this.notesEditMode = false;
            } catch (e) {
                console.error('Failed to save notes:', e);
            } finally {
                this.notesSaving = false;
            }
        },

        renderMarkdown(text) {
            if (!text) return '';
            try {
                return marked.parse(text);
            } catch (e) {
                return text;
            }
        }
    };
}

// Make components available globally for Alpine
window.cardResponse = cardResponse;
window.learningApp = learningApp;