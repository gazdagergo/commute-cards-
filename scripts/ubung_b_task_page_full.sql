-- Übung B: Full interactive task page
-- Run with: cat scripts/ubung_b_task_page_full.sql | fly postgres connect -a sociology-pwa-db -d sociology_learning_pwa

DO $$
DECLARE v_course_id INTEGER;
BEGIN
    SELECT id INTO v_course_id FROM courses WHERE slug = 'sociology';

    -- Update the existing task page with full content
    UPDATE task_pages SET
        title = 'Übung B: Forschungsartikel finden & analysieren',
        description = 'Recherchiere einen Zeitschriftenartikel zum Thema Bürgermeisterinnen und analysiere die Forschungsfrage.',
        page_html = '<!DOCTYPE html>
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
<body class="bg-gray-50">
<div class="max-w-2xl mx-auto p-4 pb-20">

<!-- Header -->
<div class="mb-6">
    <h1 class="text-2xl font-bold text-gray-800 mb-2">Übung B: Forschungsartikel analysieren</h1>
    <p class="text-gray-600 text-sm">Recherchiere und analysiere einen wissenschaftlichen Artikel zum Thema Bürgermeisterinnen</p>
</div>

<!-- Task Overview -->
<div class="bg-indigo-50 border-l-4 border-indigo-500 p-4 mb-6 rounded-r-lg">
    <h2 class="font-semibold text-indigo-800 mb-2">Aufgabenstellung</h2>
    <p class="text-indigo-700 text-sm">Schaue das Video über das Forschungsprojekt zu Bürgermeister/-innenwahlen. Nutze die genannten Informationen (Thema, Personen, Zeitschrift), um einen passenden Aufsatz zu recherchieren und zu analysieren.</p>
</div>

<!-- Quick Links -->
<div class="flex gap-3 mb-6">
    <a href="https://moodle.fernuni-hagen.de" target="_blank"
       class="flex-1 flex items-center justify-center gap-2 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        Video (Moodle)
    </a>
    <a href="https://www.fernuni-hagen.de/bibliothek/" target="_blank"
       class="flex-1 flex items-center justify-center gap-2 py-3 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/>
        </svg>
        Bibliothek
    </a>
</div>

<!-- Step 1: Video Notes -->
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
    <div class="flex items-center gap-2 mb-3">
        <span class="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">1</span>
        <h2 class="text-lg font-semibold text-gray-800">Video anschauen & Infos sammeln</h2>
    </div>
    <p class="text-gray-600 text-sm mb-4">Notiere dir beim Anschauen des Videos die wichtigsten Informationen:</p>

    <div class="space-y-3">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Thema des Forschungsprojekts</label>
            <input type="text" id="topic" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="z.B. Bürgermeisterinnen in Deutschland...">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Beteiligte Forscher*innen (mind. 2 Namen)</label>
            <input type="text" id="researchers" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="z.B. Elke Wiechmann, Benjamin Garske">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Name der genannten Zeitschrift</label>
            <input type="text" id="journal" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="z.B. Zeitschrift für...">
        </div>
    </div>
</div>

<!-- Step 2: Article Search -->
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
    <div class="flex items-center gap-2 mb-3">
        <span class="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">2</span>
        <h2 class="text-lg font-semibold text-gray-800">Artikel recherchieren</h2>
    </div>
    <p class="text-gray-600 text-sm mb-4">Suche in der Bibliothek nach einem Aufsatz, an dem mindestens 2 der genannten Personen beteiligt waren.</p>

    <div class="space-y-3">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vollständiger Titel des gefundenen Artikels</label>
            <input type="text" id="article_title" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Titel des Artikels...">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vollständige Zitation (nach LE I Vorgaben)</label>
            <textarea id="citation" rows="2" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Autor/in (Jahr): Titel. In: Zeitschrift, Jg., H., S."></textarea>
        </div>
    </div>
</div>

<!-- Step 3: Research Question -->
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
    <div class="flex items-center gap-2 mb-3">
        <span class="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">3</span>
        <h2 class="text-lg font-semibold text-gray-800">Forschungsfrage zusammenfassen</h2>
    </div>
    <p class="text-gray-600 text-sm mb-4">Lies die ersten Seiten des Artikels und fasse die Fragestellung in eigenen Worten zusammen.</p>

    <textarea id="research_question" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Die zentrale Forschungsfrage des Artikels lautet..."></textarea>
</div>

<!-- Step 4: Results -->
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
    <div class="flex items-center gap-2 mb-3">
        <span class="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">4</span>
        <h2 class="text-lg font-semibold text-gray-800">Ergebnisse zusammenfassen</h2>
    </div>
    <p class="text-gray-600 text-sm mb-4">Was sind die zentralen Erkenntnisse der Studie?</p>

    <textarea id="results" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Die Studie kommt zu folgenden Ergebnissen..."></textarea>
</div>

<!-- Step 5: Heuristics -->
<div class="bg-white rounded-xl shadow-sm p-5 mb-4">
    <div class="flex items-center gap-2 mb-3">
        <span class="w-7 h-7 bg-indigo-600 text-white rounded-full flex items-center justify-center text-sm font-bold">5</span>
        <h2 class="text-lg font-semibold text-gray-800">Begriff "Heuristiken" erklären</h2>
    </div>
    <p class="text-gray-600 text-sm mb-4">Recherchiere den Begriff in einem Lexikon und erstelle ein Exzerpt.</p>

    <div class="space-y-3">
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deine Erklärung von "Heuristiken"</label>
            <textarea id="heuristics" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Heuristiken sind..."></textarea>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Wie helfen die Literaturangaben im Aufsatz?</label>
            <textarea id="literature_help" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Die Literaturangaben helfen, weil..."></textarea>
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vollständige Zitation des genutzten Lexikons</label>
            <textarea id="lexicon_citation" rows="2" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" placeholder="Autor/in (Jahr): Stichwort. In: Lexikon..."></textarea>
        </div>
    </div>
</div>

<!-- Action Buttons -->
<div class="flex gap-3 sticky bottom-4">
    <button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200 shadow-sm">
        Entwurf speichern
    </button>
    <button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 shadow-sm">
        Abschliessen
    </button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>

</div>

<script>
const fields = [''topic'', ''researchers'', ''journal'', ''article_title'', ''citation'', ''research_question'', ''results'', ''heuristics'', ''literature_help'', ''lexicon_citation''];

document.addEventListener(''DOMContentLoaded'', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            fields.forEach(id => {
                if (saved[id] && document.getElementById(id)) {
                    document.getElementById(id).value = saved[id];
                }
            });
            showStatus(''Entwurf wiederhergestellt'', ''success'');
        }
    } catch (e) { console.log(''No draft to restore''); }
});

function getAnswers() {
    const answers = {};
    fields.forEach(id => {
        const el = document.getElementById(id);
        if (el) answers[id] = el.value;
    });
    return answers;
}

async function saveDraft() {
    const answers = getAnswers();
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus(''Entwurf gespeichert!'', ''success'');
}

async function submitAnswers() {
    const answers = getAnswers();
    const required = [''topic'', ''researchers'', ''journal'', ''research_question'', ''results''];
    const missing = required.filter(id => !answers[id] || answers[id].trim() === '''');

    if (missing.length > 0) {
        showStatus(''Bitte fülle alle Pflichtfelder aus (Schritte 1-4)'', ''error'');
        return;
    }

    await TaskAPI.submitResponse(answers);
    await TaskAPI.complete();
    showStatus(''Übung B abgeschlossen!'', ''success'');
}

function showStatus(msg, type) {
    const el = document.getElementById(''status'');
    el.textContent = msg;
    el.className = ''mt-4 text-center text-sm '' + (type === ''success'' ? ''text-green-600 font-medium'' : ''text-red-600 font-medium'');
    setTimeout(() => { el.textContent = ''''; }, 3000);
}
</script>
</body>
</html>',
        estimated_duration_minutes = 60,
        topics = ARRAY['forschungsartikel', 'literaturrecherche', 'zitieren', 'heuristik', 'exzerpt'],
        updated_at = NOW()
    WHERE id = 'ubung-b-article-analysis';

    RAISE NOTICE 'Updated task page: ubung-b-article-analysis';
END $$;
