-- Week 3-4 Task Pages and task_reference cards
-- Creates interconnected task pages with cards that reference them

DO $$
DECLARE
    v_course_id INTEGER;
BEGIN
    SELECT id INTO v_course_id FROM courses WHERE slug = 'sociology';
    IF v_course_id IS NULL THEN
        RAISE EXCEPTION 'Sociology course not found';
    END IF;

    -- =========================================================================
    -- Task Page 1: Übung B - Forschungsartikel analysieren
    -- =========================================================================

    INSERT INTO task_pages (id, title, description, page_html, course_id, topics, tags, estimated_duration_minutes, difficulty)
    VALUES (
        'ubung-b-article-analysis',
        'Übung B: Forschungsartikel analysieren',
        'Analysiere den wissenschaftlichen Artikel "Bürgermeisterinnen" und übe das Lesen von Forschungsliteratur.',
        '<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Übung B: Forschungsartikel analysieren</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
window.COMMUTE_CONFIG = {
    deviceToken: ''{{device_token}}'',
    taskPageId: ''{{task_page_id}}'',
    apiBase: ''{{api_base}}''
};
</script>
<script src="/static/js/task-api.js"></script>
</head>
<body class="bg-gray-50 p-4">
<div class="max-w-2xl mx-auto">
<h1 class="text-2xl font-bold text-gray-800 mb-2">Übung B: Forschungsartikel analysieren</h1>
<p class="text-gray-600 text-sm mb-6">Analysiere den Artikel "Bürgermeisterinnen" von Wiechmann/Garske</p>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">Aufgabe 1: Forschungsfrage identifizieren</h2>
<p class="text-gray-600 mb-4">Lies die ersten 4 Seiten des Artikels und fasse die zentrale Forschungsfrage in eigenen Worten zusammen.</p>
<textarea id="q1" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Die Forschungsfrage lautet..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">Aufgabe 2: Ergebnisse zusammenfassen</h2>
<p class="text-gray-600 mb-4">Was haben die Forscher*innen herausgefunden? Fasse die wichtigsten Ergebnisse zusammen.</p>
<textarea id="q2" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Die wichtigsten Ergebnisse sind..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">Aufgabe 3: Heuristiken erklären</h2>
<p class="text-gray-600 mb-4">Der Artikel verwendet den Begriff "Heuristiken". Erkläre in eigenen Worten, was damit gemeint ist.</p>
<textarea id="q3" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Heuristiken bedeutet..."></textarea>
</div>

<div class="flex gap-3">
<button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">Entwurf speichern</button>
<button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Abschliessen</button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>
<script>
document.addEventListener(''DOMContentLoaded'', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            if (saved.q1) document.getElementById(''q1'').value = saved.q1;
            if (saved.q2) document.getElementById(''q2'').value = saved.q2;
            if (saved.q3) document.getElementById(''q3'').value = saved.q3;
            showStatus(''Entwurf wiederhergestellt'', ''success'');
        }
    } catch (e) { console.log(''No draft''); }
});

async function saveDraft() {
    const answers = { q1: document.getElementById(''q1'').value, q2: document.getElementById(''q2'').value, q3: document.getElementById(''q3'').value };
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus(''Entwurf gespeichert!'', ''success'');
}

async function submitAnswers() {
    const answers = { q1: document.getElementById(''q1'').value, q2: document.getElementById(''q2'').value, q3: document.getElementById(''q3'').value };
    if (!answers.q1 || !answers.q2) { showStatus(''Bitte mindestens Aufgabe 1 und 2 beantworten'', ''error''); return; }
    await TaskAPI.submitResponse(answers);
    await TaskAPI.complete();
    showStatus(''Abgeschlossen!'', ''success'');
}

function showStatus(msg, type) {
    const el = document.getElementById(''status'');
    el.textContent = msg;
    el.className = ''mt-4 text-center text-sm '' + (type === ''success'' ? ''text-green-600'' : ''text-red-600'');
}
</script>
</body>
</html>',
        v_course_id,
        ARRAY['forschungsartikel', 'literaturrecherche', 'heuristik'],
        ARRAY['Week 3-4'],
        45,
        'intermediate'
    )
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        page_html = EXCLUDED.page_html,
        topics = EXCLUDED.topics,
        tags = EXCLUDED.tags,
        updated_at = NOW();

    -- Create task_reference card for Übung B
    INSERT INTO cards (card_type, task_page_id, course_id, semantic_description, visibility, card_html, response_schema, tags)
    SELECT 'task_reference', 'ubung-b-article-analysis', v_course_id,
           'Aufgabe: Übung B - Analysiere den Forschungsartikel "Bürgermeisterinnen"',
           'public', '', '{}', ARRAY['Week 3-4']
    WHERE NOT EXISTS (
        SELECT 1 FROM cards WHERE card_type = 'task_reference' AND task_page_id = 'ubung-b-article-analysis'
    );

    RAISE NOTICE 'Created task page: ubung-b-article-analysis';

    -- =========================================================================
    -- Task Page 2: Verwaltungswissenschaft Grundlagen
    -- =========================================================================

    INSERT INTO task_pages (id, title, description, page_html, course_id, topics, tags, estimated_duration_minutes, difficulty)
    VALUES (
        'verwaltungswissenschaft-basics',
        'Verwaltungswissenschaft: Grundbegriffe',
        'Teste dein Verständnis der wichtigsten Konzepte aus LE I Kapitel 4-5.',
        '<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Verwaltungswissenschaft: Grundbegriffe</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
window.COMMUTE_CONFIG = {
    deviceToken: ''{{device_token}}'',
    taskPageId: ''{{task_page_id}}'',
    apiBase: ''{{api_base}}''
};
</script>
<script src="/static/js/task-api.js"></script>
</head>
<body class="bg-gray-50 p-4">
<div class="max-w-2xl mx-auto">
<h1 class="text-2xl font-bold text-gray-800 mb-2">Verwaltungswissenschaft: Grundbegriffe</h1>
<p class="text-gray-600 text-sm mb-6">Bearbeite die folgenden Fragen zu LE I Kapitel 4-5</p>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">1. Was ist Verwaltungswissenschaft?</h2>
<p class="text-gray-600 mb-4">Erkläre in 2-3 Sätzen, was Verwaltungswissenschaft untersucht und warum sie interdisziplinär ist.</p>
<textarea id="q1" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Verwaltungswissenschaft ist..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">2. Webers Bürokratie-Begriff</h2>
<p class="text-gray-600 mb-4">Nenne drei Merkmale von Max Webers Idealtypus der Bürokratie.</p>
<textarea id="q2" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="1. ..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">3. Ebenen der Verwaltung</h2>
<p class="text-gray-600 mb-4">Welche drei Verwaltungsebenen gibt es in Deutschland? Nenne je ein Beispiel.</p>
<textarea id="q3" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Bund: z.B. ..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">4. Kommunale Selbstverwaltung</h2>
<p class="text-gray-600 mb-4">Was bedeutet kommunale Selbstverwaltung nach Art. 28 GG?</p>
<textarea id="q4" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Kommunale Selbstverwaltung bedeutet..."></textarea>
</div>

<div class="flex gap-3">
<button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">Entwurf speichern</button>
<button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Abschliessen</button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>
<script>
document.addEventListener(''DOMContentLoaded'', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            [''q1'',''q2'',''q3'',''q4''].forEach(id => { if(saved[id]) document.getElementById(id).value = saved[id]; });
            showStatus(''Entwurf wiederhergestellt'', ''success'');
        }
    } catch (e) { console.log(''No draft''); }
});

async function saveDraft() {
    const answers = {};
    [''q1'',''q2'',''q3'',''q4''].forEach(id => { answers[id] = document.getElementById(id).value; });
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus(''Entwurf gespeichert!'', ''success'');
}

async function submitAnswers() {
    const answers = {};
    [''q1'',''q2'',''q3'',''q4''].forEach(id => { answers[id] = document.getElementById(id).value; });
    if (!answers.q1 || !answers.q2) { showStatus(''Bitte mindestens Frage 1 und 2 beantworten'', ''error''); return; }
    await TaskAPI.submitResponse(answers);
    await TaskAPI.complete();
    showStatus(''Abgeschlossen!'', ''success'');
}

function showStatus(msg, type) {
    const el = document.getElementById(''status'');
    el.textContent = msg;
    el.className = ''mt-4 text-center text-sm '' + (type === ''success'' ? ''text-green-600'' : ''text-red-600'');
}
</script>
</body>
</html>',
        v_course_id,
        ARRAY['verwaltungswissenschaft', 'bürokratie', 'kommunalverwaltung'],
        ARRAY['Week 3-4'],
        30,
        'beginner'
    )
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        page_html = EXCLUDED.page_html,
        topics = EXCLUDED.topics,
        tags = EXCLUDED.tags,
        updated_at = NOW();

    -- Create task_reference card
    INSERT INTO cards (card_type, task_page_id, course_id, semantic_description, visibility, card_html, response_schema, tags)
    SELECT 'task_reference', 'verwaltungswissenschaft-basics', v_course_id,
           'Aufgabe: Verwaltungswissenschaft Grundbegriffe - Teste dein Wissen zu LE I Kap. 4-5',
           'public', '', '{}', ARRAY['Week 3-4']
    WHERE NOT EXISTS (
        SELECT 1 FROM cards WHERE card_type = 'task_reference' AND task_page_id = 'verwaltungswissenschaft-basics'
    );

    RAISE NOTICE 'Created task page: verwaltungswissenschaft-basics';

    -- =========================================================================
    -- Task Page 3: Holtkamp Vorlesung Reflexion
    -- =========================================================================

    INSERT INTO task_pages (id, title, description, page_html, course_id, topics, tags, estimated_duration_minutes, difficulty)
    VALUES (
        'holtkamp-lecture-reflection',
        'Vorlesung 2: Reflexion',
        'Reflektiere über die Vorlesung von Lars Holtkamp zur Verwaltungswissenschaft.',
        '<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vorlesung 2: Reflexion</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
window.COMMUTE_CONFIG = {
    deviceToken: ''{{device_token}}'',
    taskPageId: ''{{task_page_id}}'',
    apiBase: ''{{api_base}}''
};
</script>
<script src="/static/js/task-api.js"></script>
</head>
<body class="bg-gray-50 p-4">
<div class="max-w-2xl mx-auto">
<h1 class="text-2xl font-bold text-gray-800 mb-2">Vorlesung 2: Reflexion</h1>
<p class="text-gray-600 text-sm mb-6">Lars Holtkamp - "Was ist Verwaltungswissenschaft?"</p>

<div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
<p class="text-blue-800 text-sm"><strong>Hinweis:</strong> Schaue zuerst die Vorlesung, bevor du diese Aufgabe bearbeitest.</p>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">1. Hauptaussage</h2>
<p class="text-gray-600 mb-4">Was ist die zentrale Botschaft der Vorlesung? Was will Holtkamp vermitteln?</p>
<textarea id="q1" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Die zentrale Botschaft ist..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">2. Neue Erkenntnisse</h2>
<p class="text-gray-600 mb-4">Was hast du Neues gelernt? Was hat dich überrascht?</p>
<textarea id="q2" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Neu für mich war..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">3. Offene Fragen</h2>
<p class="text-gray-600 mb-4">Welche Fragen sind offen geblieben? Was möchtest du noch vertiefen?</p>
<textarea id="q3" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Ich möchte noch wissen..."></textarea>
</div>

<div class="flex gap-3">
<button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">Entwurf speichern</button>
<button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Abschliessen</button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>
<script>
document.addEventListener(''DOMContentLoaded'', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            [''q1'',''q2'',''q3''].forEach(id => { if(saved[id]) document.getElementById(id).value = saved[id]; });
            showStatus(''Entwurf wiederhergestellt'', ''success'');
        }
    } catch (e) { console.log(''No draft''); }
});

async function saveDraft() {
    const answers = {};
    [''q1'',''q2'',''q3''].forEach(id => { answers[id] = document.getElementById(id).value; });
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus(''Entwurf gespeichert!'', ''success'');
}

async function submitAnswers() {
    const answers = {};
    [''q1'',''q2'',''q3''].forEach(id => { answers[id] = document.getElementById(id).value; });
    if (!answers.q1) { showStatus(''Bitte mindestens Frage 1 beantworten'', ''error''); return; }
    await TaskAPI.submitResponse(answers);
    await TaskAPI.complete();
    showStatus(''Abgeschlossen!'', ''success'');
}

function showStatus(msg, type) {
    const el = document.getElementById(''status'');
    el.textContent = msg;
    el.className = ''mt-4 text-center text-sm '' + (type === ''success'' ? ''text-green-600'' : ''text-red-600'');
}
</script>
</body>
</html>',
        v_course_id,
        ARRAY['vorlesung', 'holtkamp', 'reflexion'],
        ARRAY['Week 3-4'],
        20,
        'beginner'
    )
    ON CONFLICT (id) DO UPDATE SET
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        page_html = EXCLUDED.page_html,
        topics = EXCLUDED.topics,
        tags = EXCLUDED.tags,
        updated_at = NOW();

    -- Create task_reference card
    INSERT INTO cards (card_type, task_page_id, course_id, semantic_description, visibility, card_html, response_schema, tags)
    SELECT 'task_reference', 'holtkamp-lecture-reflection', v_course_id,
           'Aufgabe: Vorlesung 2 Reflexion - Reflektiere über Holtkamps Einführung',
           'public', '', '{}', ARRAY['Week 3-4']
    WHERE NOT EXISTS (
        SELECT 1 FROM cards WHERE card_type = 'task_reference' AND task_page_id = 'holtkamp-lecture-reflection'
    );

    RAISE NOTICE 'Created task page: holtkamp-lecture-reflection';

    RAISE NOTICE 'Successfully created 3 task pages with task_reference cards for Week 3-4';
END $$;
