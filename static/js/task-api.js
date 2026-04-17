/**
 * Task API Library
 *
 * A lightweight API client for task pages to communicate with the server.
 * This library is included in every task page rendered in an iframe.
 *
 * The PWA injects configuration (deviceToken, taskPageId, apiBase) before rendering.
 *
 * Usage in task pages:
 *   TaskAPI.setStatus('in_progress')
 *   TaskAPI.submitResponse({ answers: [...] })
 *   TaskAPI.getEvaluation()
 */

const TaskAPI = {
    // Configuration injected by PWA at render time
    get config() {
        return window.COMMUTE_CONFIG || {};
    },

    /**
     * Get current status for this task page
     * @returns {Promise<{status: string, started_at: string|null, completed_at: string|null, updated_at: string|null, notes: string|null}>}
     */
    async getStatus() {
        const { apiBase, taskPageId, deviceToken } = this.config;
        if (!taskPageId || !deviceToken) {
            console.error('TaskAPI: Missing configuration');
            return { status: 'not_started' };
        }

        try {
            const response = await fetch(
                `${apiBase}/task-pages/${taskPageId}/status`,
                {
                    headers: {
                        'X-Device-Token': deviceToken
                    }
                }
            );
            return response.json();
        } catch (error) {
            console.error('TaskAPI.getStatus error:', error);
            return { status: 'not_started', error: error.message };
        }
    },

    /**
     * Update status for this task page
     * @param {string} status - One of: 'not_started', 'draft', 'in_progress', 'completed'
     * @param {string} [notes] - Optional notes to save
     * @returns {Promise<{success: boolean, status: string, started_at: string|null, completed_at: string|null}>}
     */
    async setStatus(status, notes) {
        const { apiBase, taskPageId, deviceToken } = this.config;
        if (!taskPageId || !deviceToken) {
            console.error('TaskAPI: Missing configuration');
            return { success: false, error: 'Missing configuration' };
        }

        const validStatuses = ['not_started', 'draft', 'in_progress', 'completed'];
        if (!validStatuses.includes(status)) {
            console.error('TaskAPI: Invalid status:', status);
            return { success: false, error: `Invalid status. Must be one of: ${validStatuses.join(', ')}` };
        }

        try {
            const body = { status };
            if (notes !== undefined) {
                body.notes = notes;
            }

            const response = await fetch(
                `${apiBase}/task-pages/${taskPageId}/status`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Device-Token': deviceToken
                    },
                    body: JSON.stringify(body)
                }
            );
            const result = await response.json();

            // Dispatch event for PWA to listen to
            this._dispatchEvent('statusChange', { status: result.status, ...result });

            return result;
        } catch (error) {
            console.error('TaskAPI.setStatus error:', error);
            return { success: false, error: error.message };
        }
    },

    /**
     * Submit a response for this task page
     * @param {object} content - The response content (answers, reflection, etc.)
     * @returns {Promise<{success: boolean, response_id: number, submitted_at: string}>}
     */
    async submitResponse(content) {
        const { apiBase, taskPageId, deviceToken } = this.config;
        if (!taskPageId || !deviceToken) {
            console.error('TaskAPI: Missing configuration');
            return { success: false, error: 'Missing configuration' };
        }

        try {
            const response = await fetch(
                `${apiBase}/task-pages/${taskPageId}/response`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Device-Token': deviceToken
                    },
                    body: JSON.stringify({ response_content: content })
                }
            );
            const result = await response.json();

            // Dispatch event for PWA
            this._dispatchEvent('responseSubmitted', result);

            return result;
        } catch (error) {
            console.error('TaskAPI.submitResponse error:', error);
            return { success: false, error: error.message };
        }
    },

    /**
     * Get all responses for this task page
     * @returns {Promise<{responses: Array<{id: number, submitted_at: string, response_content: object, evaluation: object|null, has_evaluation: boolean}>}>}
     */
    async getResponses() {
        const { apiBase, taskPageId, deviceToken } = this.config;
        if (!taskPageId || !deviceToken) {
            console.error('TaskAPI: Missing configuration');
            return { responses: [] };
        }

        try {
            const response = await fetch(
                `${apiBase}/task-pages/${taskPageId}/responses`,
                {
                    headers: {
                        'X-Device-Token': deviceToken
                    }
                }
            );
            return response.json();
        } catch (error) {
            console.error('TaskAPI.getResponses error:', error);
            return { responses: [], error: error.message };
        }
    },

    /**
     * Get the latest evaluation for this task page
     * @returns {Promise<{has_evaluation: boolean, evaluation: object|null, response_id: number|null, evaluated_at: string|null}>}
     */
    async getEvaluation() {
        const { apiBase, taskPageId, deviceToken } = this.config;
        if (!taskPageId || !deviceToken) {
            console.error('TaskAPI: Missing configuration');
            return { has_evaluation: false, evaluation: null };
        }

        try {
            const response = await fetch(
                `${apiBase}/task-pages/${taskPageId}/evaluation`,
                {
                    headers: {
                        'X-Device-Token': deviceToken
                    }
                }
            );
            return response.json();
        } catch (error) {
            console.error('TaskAPI.getEvaluation error:', error);
            return { has_evaluation: false, evaluation: null, error: error.message };
        }
    },

    /**
     * Convenience method: Mark task as started (in_progress)
     */
    async start() {
        return this.setStatus('in_progress');
    },

    /**
     * Convenience method: Mark task as completed
     */
    async complete() {
        return this.setStatus('completed');
    },

    /**
     * Convenience method: Save as draft
     * @param {string} [notes] - Optional draft notes
     */
    async saveDraft(notes) {
        return this.setStatus('draft', notes);
    },

    /**
     * Request navigation back to card list (communicates with parent PWA)
     */
    goBack() {
        this._dispatchEvent('navigate', { action: 'back' });
    },

    /**
     * Internal: Dispatch a custom event that the parent PWA can listen to
     * @param {string} type - Event type
     * @param {object} detail - Event detail data
     */
    _dispatchEvent(type, detail) {
        // Try postMessage for iframe communication
        try {
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: `taskPage:${type}`,
                    taskPageId: this.config.taskPageId,
                    ...detail
                }, '*');
            }
        } catch (e) {
            // Ignore cross-origin errors
        }

        // Also dispatch on window for same-origin listeners
        window.dispatchEvent(new CustomEvent(`taskPage:${type}`, {
            detail: { taskPageId: this.config.taskPageId, ...detail }
        }));
    }
};

// Auto-initialize status display if element exists
document.addEventListener('DOMContentLoaded', async () => {
    // Update status badge if element exists
    const statusEl = document.getElementById('current-status');
    if (statusEl) {
        const data = await TaskAPI.getStatus();
        statusEl.textContent = data.status || 'not_started';
        statusEl.dataset.status = data.status || 'not_started';
    }

    // Auto-mark as started if configured
    if (window.COMMUTE_CONFIG?.autoStart) {
        const currentStatus = await TaskAPI.getStatus();
        if (currentStatus.status === 'not_started') {
            await TaskAPI.start();
        }
    }
});

// Export for module environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TaskAPI;
}