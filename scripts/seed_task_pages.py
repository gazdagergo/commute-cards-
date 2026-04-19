#!/usr/bin/env python3
"""
Seed sample task pages for development/testing.
Run with: python scripts/seed_task_pages.py
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import get_db

SAMPLE_TASK_PAGE_HTML = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Soziologische Grundbegriffe</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
window.COMMUTE_CONFIG = {
    deviceToken: '{{device_token}}',
    taskPageId: '{{task_page_id}}',
    apiBase: '{{api_base}}'
};
</script>
<script src="/static/js/task-api.js"></script>
</head>
<body class="bg-gray-50 p-4">
<div class="max-w-2xl mx-auto">
<h1 class="text-2xl font-bold text-gray-800 mb-4">Soziologische Grundbegriffe</h1>
<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-3">Aufgabe</h2>
<p class="text-gray-600 mb-4">Erklaere die folgenden soziologischen Grundbegriffe in eigenen Worten:</p>
<div class="space-y-4">
<div>
<label class="block text-sm font-medium text-gray-700 mb-1">1. Was versteht man unter "Sozialisation"?</label>
<textarea id="answer1" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Deine Antwort..."></textarea>
</div>
<div>
<label class="block text-sm font-medium text-gray-700 mb-1">2. Erklaere den Begriff "soziale Rolle"</label>
<textarea id="answer2" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Deine Antwort..."></textarea>
</div>
<div>
<label class="block text-sm font-medium text-gray-700 mb-1">3. Was bedeutet "soziale Schichtung"?</label>
<textarea id="answer3" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Deine Antwort..."></textarea>
</div>
</div>
</div>
<div class="flex gap-3">
<button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">Entwurf speichern</button>
<button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Abschicken</button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>
<script>
async function saveDraft() {
    const answers = getAnswers();
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus('Entwurf gespeichert!', 'success');
}

async function submitAnswers() {
    const answers = getAnswers();
    if (!answers.answer1 && !answers.answer2 && !answers.answer3) {
        showStatus('Bitte mindestens eine Frage beantworten', 'error');
        return;
    }
    const result = await TaskAPI.submitResponse(answers);
    if (result.success) {
        await TaskAPI.complete();
        showStatus('Antworten abgeschickt!', 'success');
    } else {
        showStatus('Fehler: ' + (result.error || 'Unbekannt'), 'error');
    }
}

function getAnswers() {
    return {
        answer1: document.getElementById('answer1').value,
        answer2: document.getElementById('answer2').value,
        answer3: document.getElementById('answer3').value
    };
}

function showStatus(message, type) {
    const el = document.getElementById('status');
    el.textContent = message;
    el.className = 'mt-4 text-center text-sm ' + (type === 'success' ? 'text-green-600' : 'text-red-600');
}
</script>
</body>
</html>"""


def seed_task_pages():
    with get_db() as conn:
        with conn.cursor() as cur:
            # Update or insert the sample task page
            cur.execute("""
                INSERT INTO task_pages (id, title, description, page_html, course_id, topics, estimated_duration_minutes, difficulty)
                VALUES (%s, %s, %s, %s, 1, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    page_html = EXCLUDED.page_html,
                    estimated_duration_minutes = EXCLUDED.estimated_duration_minutes,
                    difficulty = EXCLUDED.difficulty,
                    updated_at = NOW()
            """, (
                'test-task-page-1',
                'Soziologische Grundbegriffe',
                'Erklaere wichtige soziologische Konzepte wie Sozialisation, soziale Rolle und soziale Schichtung in eigenen Worten.',
                SAMPLE_TASK_PAGE_HTML,
                ['grundbegriffe', 'sozialisation', 'soziale-rolle'],
                15,
                'beginner'
            ))
            conn.commit()
            print(f"Seeded task page: test-task-page-1")


if __name__ == '__main__':
    seed_task_pages()
    print("Done!")