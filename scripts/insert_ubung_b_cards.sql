-- Übung B Cards
-- Generated 10 cards

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Self-assess knowledge of ''Heuristik'' (heuristics) - mental shortcuts for problem-solving in research',
    'ubung-b-task4',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Heuristik</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Heuristik</strong> bezeichnet mentale Strategien oder Faustregeln, die bei der Problemlösung und Entscheidungsfindung helfen. In der Forschung sind Heuristiken vereinfachende Annahmen oder Suchstrategien, die Forscher*innen nutzen, um komplexe Probleme handhabbar zu machen – auch wenn sie nicht immer zur optimalen Lösung führen.</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? ''bg-red-600 text-white'' : ''bg-red-100 text-red-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? ''bg-yellow-600 text-white'' : ''bg-yellow-100 text-yellow-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? ''bg-green-600 text-white'' : ''bg-green-100 text-green-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gut</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Weiter</span>
                <span x-show="submitting">Wird gesendet...</span>
            </button>
        </div>
    </div>
</div>',
    '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Self-assess knowledge of ''Forschungsfrage'' (research question) - the central inquiry of a study',
    'ubung-b-task3',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Forschungsfrage</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Forschungsfrage</strong> ist die zentrale Frage, die eine wissenschaftliche Untersuchung beantworten möchte. Sie definiert den Fokus der Studie, bestimmt die Methodik und grenzt den Untersuchungsgegenstand ein. Eine gute Forschungsfrage ist präzise, beantwortbar und relevant für das Fachgebiet.</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? ''bg-red-600 text-white'' : ''bg-red-100 text-red-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? ''bg-yellow-600 text-white'' : ''bg-yellow-100 text-yellow-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? ''bg-green-600 text-white'' : ''bg-green-100 text-green-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gut</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Weiter</span>
                <span x-show="submitting">Wird gesendet...</span>
            </button>
        </div>
    </div>
</div>',
    '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Self-assess knowledge of ''Empirische Forschung'' (empirical research) - research based on observation and data',
    'ubung-b-vocab',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Empirische Forschung</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Empirische Forschung</strong> basiert auf systematischer Beobachtung und Datenerhebung. Im Gegensatz zu rein theoretischen Arbeiten sammeln empirische Studien Informationen aus der realen Welt – durch Befragungen, Experimente, Beobachtungen oder Dokumentenanalyse – um Hypothesen zu testen oder neue Erkenntnisse zu gewinnen.</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? ''bg-red-600 text-white'' : ''bg-red-100 text-red-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? ''bg-yellow-600 text-white'' : ''bg-yellow-100 text-yellow-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? ''bg-green-600 text-white'' : ''bg-green-100 text-green-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gut</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Weiter</span>
                <span x-show="submitting">Wird gesendet...</span>
            </button>
        </div>
    </div>
</div>',
    '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Identify characteristics of a journal article (Zeitschriftenartikel) vs other publication types',
    'ubung-b-task2',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Was ist ein typisches Merkmal eines Zeitschriftenartikels?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er erscheint in regelmäßigen Ausgaben einer Fachzeitschrift und durchläuft oft ein Peer-Review-Verfahren
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er umfasst immer mindestens 200 Seiten
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er wird nur von einem einzelnen Autor geschrieben
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er enthält keine Literaturverweise
            </button>
        </div>

        <button @click="submitResponse({ selected_index: selected, correct_index: 0 })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Bestätigen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>',
    '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Understand why literature references are used in research articles',
    'ubung-b-task5',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Warum sind Literaturverweise in einem Forschungsartikel wichtig?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Um den Artikel länger erscheinen zu lassen
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie belegen Quellen, ordnen die Arbeit in den Forschungsstand ein und ermöglichen Nachprüfbarkeit
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie sind nur für die Bibliothekskatalogisierung relevant
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie werden nur aus formalen Gründen verlangt
            </button>
        </div>

        <button @click="submitResponse({ selected_index: selected, correct_index: 1 })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Bestätigen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>',
    '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Fill in the blank - key element needed to find a journal article in library catalog',
    'ubung-b-task2',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '''' }">
        <p class="text-gray-600 text-sm mb-2">Ergänze den fehlenden Begriff</p>

        <p class="text-lg mb-4">
            Um einen Zeitschriftenartikel in der Bibliothek zu finden, braucht man mindestens den Namen des/der _______, den Titel der Zeitschrift und das Erscheinungsjahr.
        </p>

        <input type="text" x-model="answer"
               class="w-full p-3 border border-gray-300 rounded-lg text-center text-lg focus:ring-2 focus:ring-indigo-500"
               placeholder="Begriff eingeben">

        <p class="text-sm text-gray-500 mt-2 text-center">Hinweis: Wer hat den Artikel geschrieben?</p>

        <button @click="submitResponse({ blank_answer: answer.trim(), expected: ''Autor'' })"
                :disabled="submitting || answer.trim() === ''''"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Prüfen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>',
    '{"type": "object", "properties": {"blank_answer": {"type": "string"}, "expected": {"type": "string"}}, "required": ["blank_answer"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Fill in the blank - strategic reading technique for research articles',
    'ubung-b-task3',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '''' }">
        <p class="text-gray-600 text-sm mb-2">Ergänze den fehlenden Begriff</p>

        <p class="text-lg mb-4">
            Beim strategischen Lesen eines Forschungsartikels liest man oft zuerst den _______, um einen schnellen Überblick über Fragestellung und Ergebnisse zu bekommen.
        </p>

        <input type="text" x-model="answer"
               class="w-full p-3 border border-gray-300 rounded-lg text-center text-lg focus:ring-2 focus:ring-indigo-500"
               placeholder="Begriff eingeben">

        <p class="text-sm text-gray-500 mt-2 text-center">Hinweis: Eine kurze Zusammenfassung am Anfang des Artikels</p>

        <button @click="submitResponse({ blank_answer: answer.trim(), expected: ''Abstract'' })"
                :disabled="submitting || answer.trim() === ''''"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Prüfen</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>
    </div>
</div>',
    '{"type": "object", "properties": {"blank_answer": {"type": "string"}, "expected": {"type": "string"}}, "required": ["blank_answer"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Explain in own words how heuristics are used in research methodology',
    'ubung-b-task4',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '''' }">
        <p class="text-gray-600 text-sm mb-2">Lernziel: Heuristiken im Forschungskontext verstehen</p>
        <h2 class="text-lg font-semibold mb-4">Erkläre in eigenen Worten: Wie können Heuristiken Forscher*innen bei der Analyse komplexer Daten helfen?</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="5"
                  placeholder="Schreibe deine Antwort..."></textarea>

        <button @click="submitResponse({ answer })"
                :disabled="submitting || answer.trim().length < 20"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>',
    '{"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Practice summarizing research findings in clear, concise language',
    'ubung-b-task3',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '''' }">
        <p class="text-gray-600 text-sm mb-2">Lernziel: Forschungsergebnisse verständlich zusammenfassen</p>
        <h2 class="text-lg font-semibold mb-4">Stell dir vor, du hast einen Artikel über "Bürgermeisterinnen in Deutschland" gelesen. Was wären wichtige Aspekte, die du bei einer Zusammenfassung der Forschungsergebnisse erwähnen würdest?</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="5"
                  placeholder="Denke an: Was wurde untersucht? Welche Methode? Was wurde gefunden?"></textarea>

        <button @click="submitResponse({ answer })"
                :disabled="submitting || answer.trim().length < 30"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>',
    '{"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}'::jsonb,
    'public',
    'learning'
);

INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type)
VALUES (
    'Übung B: Self-assess knowledge of ''Exzerpt'' (excerpt) - a selective summary of a text',
    'ubung-b-vocab',
    '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Exzerpt</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Exzerpt</strong> ist eine schriftliche Zusammenfassung der wichtigsten Inhalte eines Textes in eigenen Worten. Es dient dazu, Kernaussagen festzuhalten, das Verständnis zu sichern und später auf die Informationen zurückgreifen zu können – ohne den Originaltext erneut lesen zu müssen.</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? ''bg-red-600 text-white'' : ''bg-red-100 text-red-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? ''bg-yellow-600 text-white'' : ''bg-yellow-100 text-yellow-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? ''bg-green-600 text-white'' : ''bg-green-100 text-green-800''"
                        class="flex-1 py-2 rounded-lg text-sm">Gut</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Weiter</span>
                <span x-show="submitting">Wird gesendet...</span>
            </button>
        </div>
    </div>
</div>',
    '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}'::jsonb,
    'public',
    'learning'
);
