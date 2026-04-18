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

        // Settings state
        settingsOpen: false,
        availableCourses: [],
        subscribedCourses: [],

        // Draft state
        currentDraft: null,
        savingDraft: false,

        /**
         * Initialize on mount
         */
        async init() {
            await initApp();
            this.initialized = true;

            // Load subscribed courses
            this.subscribedCourses = await db.getSubscribedCourses();

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
            this.currentDraft = null;

            try {
                // Get next card from local database
                const card = await db.getNextCard();

                if (card) {
                    // Load notes and draft for this card
                    const notes = await db.getNotes(card.id);
                    const draft = await db.getDraft(card.id);
                    this.currentCard = { ...card, notes };
                    this.currentDraft = draft;

                    // If there's a draft, restore it after DOM updates
                    if (draft) {
                        this.$nextTick(() => this.restoreDraft());
                    }
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
        async onCardSubmitted(message, localId) {
            this.successMessage = message || 'Gespeichert';
            this.currentLocalId = localId;
            this.showFeedback = true;

            // Clear draft since the card was submitted
            if (this.currentCard) {
                await db.clearDraft(this.currentCard.id);
                this.currentDraft = null;
            }
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
        },

        // =================================================================
        // Settings methods
        // =================================================================

        async openSettings() {
            this.settingsOpen = true;

            // Fetch available courses from server
            try {
                const response = await fetch('/api/courses');
                if (response.ok) {
                    const data = await response.json();
                    this.availableCourses = data.courses || [];
                }
            } catch (e) {
                console.error('Failed to fetch courses:', e);
            }
        },

        closeSettings() {
            this.settingsOpen = false;
        },

        async toggleCourse(slug) {
            // Toggle in local state
            const index = this.subscribedCourses.indexOf(slug);
            if (index >= 0) {
                this.subscribedCourses.splice(index, 1);
            } else {
                this.subscribedCourses.push(slug);
            }

            // Persist to IndexedDB
            await db.setSubscribedCourses([...this.subscribedCourses]);

            // Clear local cards and re-fetch based on new subscriptions
            await this.refreshCardsForSubscriptions();
        },

        async refreshCardsForSubscriptions() {
            // Clear existing cards from IndexedDB
            await db.clearCards();

            // Fetch new cards based on current subscriptions
            if (sync.syncState.isOnline) {
                await sync.fetchInitialCards();
            }

            // Reload current card
            await this.loadNextCard();
        },

        // =================================================================
        // Draft methods
        // =================================================================

        /**
         * Capture current form state from card inputs
         */
        captureFormState() {
            const cardContainer = document.getElementById('card-content');
            if (!cardContainer) return null;

            const formData = {};
            let hasContent = false;

            // Capture all input values
            const inputs = cardContainer.querySelectorAll('input, textarea, select');
            inputs.forEach((input, index) => {
                const key = input.name || `input_${index}`;

                if (input.type === 'radio') {
                    if (input.checked) {
                        formData[input.name] = input.value;
                        hasContent = true;
                    }
                } else if (input.type === 'checkbox') {
                    if (!formData[key]) formData[key] = [];
                    if (input.checked) {
                        formData[key].push(input.value);
                        hasContent = true;
                    }
                } else {
                    const value = input.value?.trim();
                    if (value) {
                        formData[key] = value;
                        hasContent = true;
                    }
                }
            });

            return hasContent ? formData : null;
        },

        /**
         * Restore draft values to form inputs
         */
        restoreDraft() {
            if (!this.currentDraft?.form_data) return;

            const cardContainer = document.getElementById('card-content');
            if (!cardContainer) return;

            const formData = this.currentDraft.form_data;

            // Restore values to inputs
            const inputs = cardContainer.querySelectorAll('input, textarea, select');
            inputs.forEach((input, index) => {
                const key = input.name || `input_${index}`;

                if (input.type === 'radio') {
                    if (formData[input.name] === input.value) {
                        input.checked = true;
                        // Trigger change event for Alpine reactivity
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                } else if (input.type === 'checkbox') {
                    const values = formData[key] || [];
                    if (values.includes(input.value)) {
                        input.checked = true;
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                } else if (formData[key]) {
                    input.value = formData[key];
                    // Trigger input event for Alpine reactivity
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });

            console.log('Draft restored for card', this.currentCard?.id);
        },

        /**
         * Save current work as draft and move to next card
         */
        async saveDraftAndContinue() {
            if (!this.currentCard || this.savingDraft) return;

            this.savingDraft = true;

            try {
                const formData = this.captureFormState();

                if (formData) {
                    await db.saveDraft(this.currentCard.id, formData);
                    console.log('Draft saved for card', this.currentCard.id);
                }

                // Move to next card (draft cards will come back later)
                await this.loadNextCard();

            } catch (e) {
                console.error('Failed to save draft:', e);
            } finally {
                this.savingDraft = false;
            }
        },

        /**
         * Clear draft for current card
         */
        async clearCurrentDraft() {
            if (!this.currentCard) return;

            await db.clearDraft(this.currentCard.id);
            this.currentDraft = null;
        }
    };
}

/**
 * Task page view component
 * Handles displaying task pages in iframes and managing their state
 */
export function taskPageView() {
    return {
        // Task page state
        taskPageId: null,
        taskPage: null,
        taskPageHtml: null,
        loading: true,
        error: null,

        // Status
        status: null,

        /**
         * Load a task page by ID
         */
        async loadTaskPage(id) {
            this.taskPageId = id;
            this.loading = true;
            this.error = null;
            this.taskPage = null;
            this.taskPageHtml = null;

            try {
                // Try to get from cache first
                let taskPage = await db.getTaskPage(id);

                if (!taskPage) {
                    // Fetch from server
                    const deviceToken = await db.getOrCreateDeviceToken();
                    const response = await fetch(`/api/task-pages/${id}`, {
                        headers: { 'X-Device-Token': deviceToken }
                    });

                    if (!response.ok) {
                        throw new Error('Task page not found');
                    }

                    taskPage = await response.json();

                    // Cache it (without HTML for now)
                    await db.saveTaskPage(taskPage);
                }

                this.taskPage = taskPage;

                // Get status from local DB
                this.status = await db.getTaskPageStatus(id);

                // Fetch HTML content
                const htmlResponse = await fetch(`/api/task-pages/${id}/html`);
                if (htmlResponse.ok) {
                    this.taskPageHtml = await htmlResponse.text();
                }

                this.loading = false;

                // Render in iframe after DOM update
                this.$nextTick(() => this.renderInIframe());

            } catch (e) {
                console.error('Failed to load task page:', e);
                this.error = e.message;
                this.loading = false;
            }
        },

        /**
         * Render task page HTML in iframe with injected config
         */
        async renderInIframe() {
            const iframe = this.$refs.taskFrame;
            if (!iframe || !this.taskPageHtml) return;

            const deviceToken = await db.getOrCreateDeviceToken();

            // Inject config into HTML
            let html = this.taskPageHtml;
            html = html.replace(/\{\{device_token\}\}/g, deviceToken);
            html = html.replace(/\{\{task_page_id\}\}/g, this.taskPageId);
            html = html.replace(/\{\{api_base\}\}/g, '/api');

            // Use srcdoc to render
            iframe.srcdoc = html;
        },

        /**
         * Update task page status (locally and queue for sync)
         */
        async updateStatus(newStatus) {
            if (!this.taskPageId) return;

            try {
                // Update locally
                this.status = await db.updateTaskPageStatus(this.taskPageId, newStatus);

                // Queue for sync if online, otherwise just save locally
                if (navigator.onLine) {
                    const deviceToken = await db.getOrCreateDeviceToken();
                    await fetch(`/api/task-pages/${this.taskPageId}/status`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-Device-Token': deviceToken
                        },
                        body: JSON.stringify({ status: newStatus })
                    });
                } else {
                    // Queue for later sync
                    await db.queueTaskUpdate(this.taskPageId, newStatus);
                }

                console.log('Task page status updated:', newStatus);
            } catch (e) {
                console.error('Failed to update status:', e);
            }
        },

        /**
         * Get status badge class
         */
        getStatusBadgeClass(status) {
            const classes = {
                'not_started': 'bg-gray-100 text-gray-600',
                'draft': 'bg-amber-100 text-amber-700',
                'in_progress': 'bg-blue-100 text-blue-700',
                'completed': 'bg-green-100 text-green-700'
            };
            return classes[status] || classes['not_started'];
        },

        /**
         * Get status display text
         */
        getStatusText(status) {
            const texts = {
                'not_started': 'Nicht gestartet',
                'draft': 'Entwurf',
                'in_progress': 'In Bearbeitung',
                'completed': 'Abgeschlossen'
            };
            return texts[status] || texts['not_started'];
        }
    };
}

/**
 * Task pages list component
 * Shows available task pages with their statuses
 */
export function taskPagesList() {
    return {
        taskPages: [],
        loading: true,
        error: null,

        async init() {
            await this.loadTaskPages();
        },

        async loadTaskPages() {
            this.loading = true;
            this.error = null;

            try {
                const deviceToken = await db.getOrCreateDeviceToken();

                // Fetch from server
                const response = await fetch('/api/task-pages', {
                    headers: { 'X-Device-Token': deviceToken }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch task pages');
                }

                const data = await response.json();
                this.taskPages = data.task_pages || [];

                // Cache task pages locally (without full HTML)
                await db.saveTaskPages(this.taskPages);

                // Also save statuses locally
                const statuses = this.taskPages
                    .filter(tp => tp.status)
                    .map(tp => ({
                        task_page_id: tp.id,
                        status: tp.status.status,
                        started_at: tp.status.started_at,
                        completed_at: tp.status.completed_at,
                        updated_at: tp.status.updated_at
                    }));
                if (statuses.length > 0) {
                    await db.saveTaskPageStatuses(statuses);
                }

            } catch (e) {
                console.error('Failed to load task pages:', e);
                this.error = e.message;

                // Try to load from cache
                this.taskPages = await db.getAllTaskPages();
            } finally {
                this.loading = false;
            }
        },

        getStatusBadgeClass(taskPage) {
            const status = taskPage.status?.status || 'not_started';
            const classes = {
                'not_started': 'bg-gray-100 text-gray-600',
                'draft': 'bg-amber-100 text-amber-700',
                'in_progress': 'bg-blue-100 text-blue-700',
                'completed': 'bg-green-100 text-green-700'
            };
            return classes[status] || classes['not_started'];
        },

        getStatusText(taskPage) {
            const status = taskPage.status?.status || 'not_started';
            const texts = {
                'not_started': 'Nicht gestartet',
                'draft': 'Entwurf',
                'in_progress': 'In Bearbeitung',
                'completed': 'Abgeschlossen'
            };
            return texts[status] || texts['not_started'];
        }
    };
}

// Make components available globally for Alpine
window.cardResponse = cardResponse;
window.learningApp = learningApp;
window.taskPageView = taskPageView;
window.taskPagesList = taskPagesList;