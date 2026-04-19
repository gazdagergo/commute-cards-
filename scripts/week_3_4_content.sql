-- Week 3-4 Content: Administrative Science Introduction
-- Generated SQL for direct database insertion

-- Get sociology course ID (should be 1)
DO $$
DECLARE
    v_course_id INTEGER;
BEGIN
    SELECT id INTO v_course_id FROM courses WHERE slug = 'sociology';
    IF v_course_id IS NULL THEN
        RAISE EXCEPTION 'Sociology course not found';
    END IF;

    -- =========================================================================
    -- LE I Chapter 4-5: Administrative Science (Verwaltungswissenschaft)
    -- =========================================================================

    -- Card: Self-assessment - Verwaltungswissenschaft
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Self-assess knowledge of ''Verwaltungswissenschaft'' (Administrative Science)',
        'le1-ch4-vocab',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Verwaltungswissenschaft</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Verwaltungswissenschaft</strong> ist die wissenschaftliche Disziplin, die sich mit der öffentlichen Verwaltung befasst. Sie untersucht Strukturen, Prozesse und Funktionen von Behörden und staatlichen Institutionen. Als interdisziplinäres Fach verbindet sie Elemente aus Politikwissenschaft, Rechtswissenschaft, Soziologie und Betriebswirtschaftslehre.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Bürokratie
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Self-assess knowledge of ''Bürokratie'' (Bureaucracy) - Max Weber''s ideal type',
        'le1-ch4-vocab',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Bürokratie</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Bürokratie</strong> bezeichnet nach Max Weber einen Idealtypus rationaler Herrschaft, gekennzeichnet durch: Amtshierarchie, Aktenmäßigkeit, Regelgebundenheit, Fachschulung und hauptberufliche Tätigkeit. Weber sah die Bürokratie als technisch überlegene Organisationsform, erkannte aber auch ihre Schattenseiten (Entpersönlichung, Starrheit).</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Multiple choice - Public vs Private Administration
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Identify characteristics that distinguish public administration from private organizations',
        'le1-ch4',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Was unterscheidet die öffentliche Verwaltung von privaten Unternehmen?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie ist an Gesetze und das Gemeinwohl gebunden, nicht primär an Gewinnmaximierung
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie hat immer mehr Mitarbeiter
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie arbeitet schneller und effizienter
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie hat keine Hierarchie
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Kommunalverwaltung
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Self-assess knowledge of ''Kommunalverwaltung'' (Municipal Administration)',
        'le1-ch5-vocab',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Kommunalverwaltung</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Kommunalverwaltung</strong> umfasst die Verwaltung auf Gemeinde- und Kreisebene. Sie ist für lokale Aufgaben wie Bauplanung, Schulen, Sozialleistungen und öffentliche Einrichtungen zuständig. In Deutschland genießen Kommunen das Recht auf Selbstverwaltung (Art. 28 GG), sind aber auch an Bundes- und Landesgesetze gebunden.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Multiple choice - German Administration Levels
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Identify the correct levels of German public administration',
        'le1-ch5',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Welche Verwaltungsebenen gibt es in Deutschland?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Bundes- und Landesverwaltung
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Bund, Länder und Kommunen (dreistufig)
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur eine zentrale Bundesverwaltung
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Bund, EU, Kommunen
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- =========================================================================
    -- Lecture 2: Lars Holtkamp
    -- =========================================================================

    -- Card: Multiple choice - Interdisciplinary nature
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Identify disciplines that contribute to Verwaltungswissenschaft',
        'lecture2-holtkamp',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Vorlesung 2: Lars Holtkamp</p>
        <h2 class="text-lg font-semibold mb-4">Verwaltungswissenschaft ist interdisziplinär. Welche Fächer tragen zu ihr bei?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Rechtswissenschaft
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Politikwissenschaft, Rechtswissenschaft, Soziologie und BWL
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Politikwissenschaft und Geschichte
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Mathematik und Informatik
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- =========================================================================
    -- Article 2: Bürgermeisterinnen
    -- =========================================================================

    -- Card: Self-assessment - Repräsentation
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Self-assess knowledge of ''Repräsentation'' (Representation) in political context',
        'article2-vocab',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Repräsentation</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Repräsentation</strong> bezeichnet in der Politikwissenschaft die Vertretung von Bürger*innen durch gewählte Amtsträger*innen. Man unterscheidet deskriptive Repräsentation (Übereinstimmung sozialer Merkmale wie Geschlecht) und substantielle Repräsentation (Vertretung von Interessen). Die Frage nach Frauenrepräsentation in politischen Ämtern ist ein wichtiges Forschungsfeld.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Multiple choice - Gender in local politics
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Week 3-4: Understand why female mayors are underrepresented in Germany',
        'article2',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Artikel: Bürgermeisterinnen</p>
        <h2 class="text-lg font-semibold mb-4">Was ist ein möglicher Grund für den geringen Anteil von Bürgermeisterinnen in Deutschland?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Frauen interessieren sich nicht für Politik
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Strukturelle Barrieren wie Vereinbarkeit von Amt und Familie, Rekrutierungsmuster der Parteien
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Es gibt keine Bürgermeisterinnen
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? ''border-indigo-600 bg-indigo-50'' : ''border-gray-300''"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Frauen dürfen erst seit kurzem kandidieren
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- =========================================================================
    -- Übung B Cards
    -- =========================================================================

    -- Card: Self-assessment - Heuristik
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
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
                <p class="text-gray-800"><strong>Heuristik</strong> bezeichnet mentale Strategien oder Faustregeln, die bei der Problemlösung und Entscheidungsfindung helfen. In der Forschung sind Heuristiken vereinfachende Annahmen oder Suchstrategien, die Forscher*innen nutzen, um komplexe Probleme handhabbar zu machen.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Forschungsfrage
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Übung B: Self-assess knowledge of ''Forschungsfrage'' (research question)',
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
                <p class="text-gray-800"><strong>Forschungsfrage</strong> ist die zentrale Frage, die eine wissenschaftliche Untersuchung beantworten möchte. Sie definiert den Fokus der Studie, bestimmt die Methodik und grenzt den Untersuchungsgegenstand ein. Eine gute Forschungsfrage ist präzise, beantwortbar und relevant.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Empirische Forschung
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Übung B: Self-assess knowledge of ''Empirische Forschung'' (empirical research)',
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
                <p class="text-gray-800"><strong>Empirische Forschung</strong> basiert auf systematischer Beobachtung und Datenerhebung. Im Gegensatz zu rein theoretischen Arbeiten sammeln empirische Studien Informationen aus der realen Welt – durch Befragungen, Experimente, Beobachtungen oder Dokumentenanalyse.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Exzerpt
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Übung B: Self-assess knowledge of ''Exzerpt'' (excerpt) - a selective summary',
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
                <p class="text-gray-800"><strong>Exzerpt</strong> ist eine schriftliche Zusammenfassung der wichtigsten Inhalte eines Textes in eigenen Worten. Es dient dazu, Kernaussagen festzuhalten, das Verständnis zu sichern und später auf die Informationen zurückgreifen zu können.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Self-assessment - Peer Review
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Übung B: Self-assess knowledge of ''Peer Review'' - the academic review process',
        'ubung-b-vocab',
        '<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Peer Review</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Peer Review</strong> (Begutachtungsverfahren) ist der Prozess, bei dem eingereichte wissenschaftliche Artikel von anderen Fachleuten (Peers) vor der Veröffentlichung geprüft werden. Die Gutachter*innen bewerten Methodik, Argumentation und Relevanz.</p>
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
        '{"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Multiple choice - Zeitschriftenartikel
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
    VALUES (
        'Übung B: Identify characteristics of a journal article (Zeitschriftenartikel)',
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    -- Card: Multiple choice - Literature references
    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
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
        '{"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}',
        'public',
        'learning',
        v_course_id,
        ARRAY['Week 3-4']
    );

    RAISE NOTICE 'Inserted 16 Week 3-4 cards successfully';
END $$;
