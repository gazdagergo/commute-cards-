#!/usr/bin/env python3
"""
Insert Week 3-4 learning cards and task pages into the database.

Week 3-4 Theme: Administrative Science Introduction
- LE I Chapters 4-5: Administrative Science fundamentals
- Lecture 2: Lars Holtkamp - "Was ist Verwaltungswissenschaft?"
- Article 2: Elke Wiechmann/Benjamin Garske - "Bürgermeisterinnen"
- Übung B: Research Article Analysis & Journal Discovery

Run with: python scripts/insert_week_3_4_content.py
Requires DATABASE_URL environment variable.
"""

import os
import json
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/sociology_learning_pwa")

# =============================================================================
# CARDS - All tagged with "Week 3-4"
# =============================================================================

cards = [
    # =========================================================================
    # LE I Chapter 4-5: Administrative Science (Verwaltungswissenschaft)
    # =========================================================================

    # Card: Self-assessment - Verwaltungswissenschaft
    {
        "semantic_description": "Week 3-4: Self-assess knowledge of 'Verwaltungswissenschaft' (Administrative Science)",
        "course_task_ref": "le1-ch4-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card: Self-assessment - Bürokratie
    {
        "semantic_description": "Week 3-4: Self-assess knowledge of 'Bürokratie' (Bureaucracy) - Max Weber's ideal type",
        "course_task_ref": "le1-ch4-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card: Multiple choice - Characteristics of Public Administration
    {
        "semantic_description": "Week 3-4: Identify characteristics that distinguish public administration from private organizations",
        "course_task_ref": "le1-ch4",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Was unterscheidet die öffentliche Verwaltung von privaten Unternehmen?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie ist an Gesetze und das Gemeinwohl gebunden, nicht primär an Gewinnmaximierung
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie hat immer mehr Mitarbeiter
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie arbeitet schneller und effizienter
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card: Self-assessment - Kommunalverwaltung
    {
        "semantic_description": "Week 3-4: Self-assess knowledge of 'Kommunalverwaltung' (Municipal Administration)",
        "course_task_ref": "le1-ch5-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card: Multiple choice - Levels of German Administration
    {
        "semantic_description": "Week 3-4: Identify the correct levels of German public administration",
        "course_task_ref": "le1-ch5",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Welche Verwaltungsebenen gibt es in Deutschland?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Bundes- und Landesverwaltung
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Bund, Länder und Kommunen (dreistufig)
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur eine zentrale Bundesverwaltung
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # =========================================================================
    # Lecture 2: Lars Holtkamp - "Was ist Verwaltungswissenschaft?"
    # =========================================================================

    # Card: Free text - Definition of Verwaltungswissenschaft
    {
        "semantic_description": "Week 3-4: Explain in own words what Verwaltungswissenschaft studies based on Holtkamp's lecture",
        "course_task_ref": "lecture2-holtkamp",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Vorlesung 2: Lars Holtkamp</p>
        <h2 class="text-lg font-semibold mb-4">Was ist der Gegenstand der Verwaltungswissenschaft? Erkläre in eigenen Worten, was diese Disziplin untersucht.</h2>

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
</div>''',
        "response_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
    },

    # Card: Multiple choice - Interdisciplinary nature
    {
        "semantic_description": "Week 3-4: Identify disciplines that contribute to Verwaltungswissenschaft",
        "course_task_ref": "lecture2-holtkamp",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Vorlesung 2: Lars Holtkamp</p>
        <h2 class="text-lg font-semibold mb-4">Verwaltungswissenschaft ist interdisziplinär. Welche Fächer tragen zu ihr bei?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Rechtswissenschaft
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Politikwissenschaft, Rechtswissenschaft, Soziologie und BWL
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur Politikwissenschaft und Geschichte
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # =========================================================================
    # Article 2: "Bürgermeisterinnen" (Female Mayors)
    # =========================================================================

    # Card: Self-assessment - Repräsentation
    {
        "semantic_description": "Week 3-4: Self-assess knowledge of 'Repräsentation' (Representation) in political context",
        "course_task_ref": "article2-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card: Free text - Research question about Bürgermeisterinnen
    {
        "semantic_description": "Week 3-4: Formulate what the research question of the Bürgermeisterinnen study might be",
        "course_task_ref": "article2-question",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Artikel: Bürgermeisterinnen (Wiechmann/Garske)</p>
        <h2 class="text-lg font-semibold mb-4">Was könnte die zentrale Forschungsfrage der Studie über Bürgermeisterinnen sein? Formuliere eine mögliche Forschungsfrage.</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="4"
                  placeholder="z.B.: Welche Faktoren beeinflussen..."></textarea>

        <button @click="submitResponse({ answer })"
                :disabled="submitting || answer.trim().length < 15"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed">
            <span x-show="!submitting">Antwort senden</span>
            <span x-show="submitting">Wird gesendet...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
    },

    # Card: Multiple choice - Gender in local politics
    {
        "semantic_description": "Week 3-4: Understand why female mayors are underrepresented in Germany",
        "course_task_ref": "article2",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Artikel: Bürgermeisterinnen</p>
        <h2 class="text-lg font-semibold mb-4">Was ist ein möglicher Grund für den geringen Anteil von Bürgermeisterinnen in Deutschland?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Frauen interessieren sich nicht für Politik
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Strukturelle Barrieren wie Vereinbarkeit von Amt und Familie, Rekrutierungsmuster der Parteien
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Es gibt keine Bürgermeisterinnen
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # =========================================================================
    # Übung B: Research Article Analysis & Journal Discovery
    # =========================================================================

    # Card 1: Self-assessment - Heuristik definition
    {
        "semantic_description": "Übung B: Self-assess knowledge of 'Heuristik' (heuristics) - mental shortcuts for problem-solving in research",
        "course_task_ref": "ubung-b-task4",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 2: Self-assessment - Forschungsfrage
    {
        "semantic_description": "Übung B: Self-assess knowledge of 'Forschungsfrage' (research question) - the central inquiry of a study",
        "course_task_ref": "ubung-b-task3",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 3: Self-assessment - Empirische Forschung
    {
        "semantic_description": "Übung B: Self-assess knowledge of 'Empirische Forschung' (empirical research) - research based on observation and data",
        "course_task_ref": "ubung-b-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 4: Multiple choice - What is a Zeitschriftenartikel?
    {
        "semantic_description": "Übung B: Identify characteristics of a journal article (Zeitschriftenartikel) vs other publication types",
        "course_task_ref": "ubung-b-task2",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Was ist ein typisches Merkmal eines Zeitschriftenartikels?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er erscheint in regelmäßigen Ausgaben einer Fachzeitschrift und durchläuft oft ein Peer-Review-Verfahren
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er umfasst immer mindestens 200 Seiten
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Er wird nur von einem einzelnen Autor geschrieben
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card 5: Multiple choice - Purpose of literature references
    {
        "semantic_description": "Übung B: Understand why literature references are used in research articles",
        "course_task_ref": "ubung-b-task5",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Warum sind Literaturverweise in einem Forschungsartikel wichtig?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Um den Artikel länger erscheinen zu lassen
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie belegen Quellen, ordnen die Arbeit in den Forschungsstand ein und ermöglichen Nachprüfbarkeit
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Sie sind nur für die Bibliothekskatalogisierung relevant
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card 6: Self-assessment - Exzerpt
    {
        "semantic_description": "Übung B: Self-assess knowledge of 'Exzerpt' (excerpt) - a selective summary of a text",
        "course_task_ref": "ubung-b-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 7: Self-assessment - Peer Review
    {
        "semantic_description": "Übung B: Self-assess knowledge of 'Peer Review' - the academic review process",
        "course_task_ref": "ubung-b-vocab",
        "tags": ["Week 3-4"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
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
                <p class="text-gray-800"><strong>Peer Review</strong> (Begutachtungsverfahren) ist der Prozess, bei dem eingereichte wissenschaftliche Artikel von anderen Fachleuten (Peers) vor der Veröffentlichung geprüft werden. Die Gutachter*innen bewerten Methodik, Argumentation und Relevanz und geben Empfehlungen zur Annahme, Überarbeitung oder Ablehnung.</p>
            </div>

            <p class="text-center text-sm text-gray-600">Wie gut wusstest du das?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Gar nicht</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Teilweise</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
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
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },
]

# =============================================================================
# TASK PAGES
# =============================================================================

task_pages = [
    {
        "id": "ubung-b-article-analysis",
        "title": "Übung B: Forschungsartikel analysieren",
        "description": "Analysiere einen wissenschaftlichen Artikel über Bürgermeisterinnen und übe das Lesen von Forschungsliteratur.",
        "tags": ["Week 3-4"],
        "topics": ["forschungsartikel", "literaturrecherche", "zitieren"],
        "estimated_duration_minutes": 45,
        "difficulty": "intermediate",
        "page_html": '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Übung B: Forschungsartikel analysieren</title>
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
<p class="text-gray-600 mb-4">Der Artikel verwendet den Begriff "Heuristiken". Erkläre in eigenen Worten, was damit gemeint ist und warum er für diese Forschung relevant ist.</p>
<textarea id="q3" rows="4" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Heuristiken bedeutet..."></textarea>
</div>

<div class="bg-white rounded-lg shadow-sm p-6 mb-4">
<h2 class="text-lg font-semibold text-gray-700 mb-4">Aufgabe 4: Literaturverweise nutzen</h2>
<p class="text-gray-600 mb-4">Wie helfen die Literaturverweise im Artikel beim Verständnis? Nenne mindestens zwei Funktionen.</p>
<textarea id="q4" rows="3" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500" placeholder="Die Literaturverweise helfen, weil..."></textarea>
</div>

<div class="flex gap-3">
<button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">Entwurf speichern</button>
<button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">Abschicken</button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>
<script>
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            if (saved.q1) document.getElementById('q1').value = saved.q1;
            if (saved.q2) document.getElementById('q2').value = saved.q2;
            if (saved.q3) document.getElementById('q3').value = saved.q3;
            if (saved.q4) document.getElementById('q4').value = saved.q4;
            showStatus('Entwurf wiederhergestellt', 'success');
        }
    } catch (e) {
        console.log('No draft to restore:', e);
    }
});

async function saveDraft() {
    const answers = getAnswers();
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus('Entwurf gespeichert!', 'success');
}

async function submitAnswers() {
    const answers = getAnswers();
    if (!answers.q1 || !answers.q2) {
        showStatus('Bitte mindestens Aufgabe 1 und 2 beantworten', 'error');
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
        q1: document.getElementById('q1').value,
        q2: document.getElementById('q2').value,
        q3: document.getElementById('q3').value,
        q4: document.getElementById('q4').value
    };
}

function showStatus(message, type) {
    const el = document.getElementById('status');
    el.textContent = message;
    el.className = 'mt-4 text-center text-sm ' + (type === 'success' ? 'text-green-600' : 'text-red-600');
}
</script>
</body>
</html>'''
    },
]


def insert_content():
    """Insert all Week 3-4 content into the database."""
    conn = psycopg.connect(DATABASE_URL)

    with conn:
        with conn.cursor() as cur:
            # Get sociology course ID
            cur.execute("SELECT id FROM courses WHERE slug = 'sociology'")
            row = cur.fetchone()
            if not row:
                print("Error: sociology course not found")
                return
            course_id = row[0]

            # Insert cards
            cards_inserted = 0
            for card in cards:
                cur.execute("""
                    INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, course_id, tags)
                    VALUES (%s, %s, %s, %s, 'public', 'learning', %s, %s)
                """, (
                    card["semantic_description"],
                    card["course_task_ref"],
                    card["card_html"],
                    json.dumps(card["response_schema"]),
                    course_id,
                    card["tags"]
                ))
                cards_inserted += 1

            print(f"Inserted {cards_inserted} cards")

            # Insert task pages
            task_pages_inserted = 0
            for page in task_pages:
                cur.execute("""
                    INSERT INTO task_pages (id, title, description, page_html, course_id, topics, tags, estimated_duration_minutes, difficulty)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        page_html = EXCLUDED.page_html,
                        topics = EXCLUDED.topics,
                        tags = EXCLUDED.tags,
                        estimated_duration_minutes = EXCLUDED.estimated_duration_minutes,
                        difficulty = EXCLUDED.difficulty,
                        updated_at = NOW()
                """, (
                    page["id"],
                    page["title"],
                    page["description"],
                    page["page_html"],
                    course_id,
                    page["topics"],
                    page["tags"],
                    page["estimated_duration_minutes"],
                    page["difficulty"]
                ))
                task_pages_inserted += 1

                # Create task_reference card for this task page
                cur.execute("""
                    SELECT id FROM cards WHERE card_type = 'task_reference' AND task_page_id = %s
                """, (page["id"],))
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO cards (card_type, task_page_id, course_id, semantic_description, visibility, card_html, response_schema, tags)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        'task_reference',
                        page["id"],
                        course_id,
                        f'Aufgabe: {page["title"]}',
                        'public',
                        '',
                        '{}',
                        page["tags"]
                    ))
                    print(f"Created task_reference card for {page['id']}")

            print(f"Inserted/updated {task_pages_inserted} task pages")

        conn.commit()

    print("Done!")


if __name__ == '__main__':
    insert_content()
