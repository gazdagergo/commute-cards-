#!/usr/bin/env python3
"""
Insert Week 5-6 learning cards and task pages into the database.

Week 5-6 Theme: Themenfelder in den Sozialwissenschaften (LE IV)
- Kapitel 1: Einleitung - Overview of social science themes
- Kapitel 2: Macht (Power) - Weber's and Arendt's concepts of power
- Übung C: Using Lexicons and Reference Works

Content from: Themenfelder in den Sozialwissenschaften (Studienbrief LE IV)

Run with: python scripts/insert_week_5_6_content.py
Requires DATABASE_URL environment variable.
"""

import os
import json
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/sociology_learning_pwa")

# =============================================================================
# CARDS - All tagged with "Week 5-6"
# =============================================================================

cards = [
    # =========================================================================
    # Kapitel 2: Macht (Power) - Max Weber's Concepts
    # =========================================================================

    # Card 1: Self-assessment - Macht (Weber)
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of Max Weber's definition of 'Macht' (power)",
        "course_task_ref": "le4-ch2-macht",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Macht (nach Weber)</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Macht</strong> bedeutet nach Max Weber „jede Chance, innerhalb einer sozialen Beziehung den eigenen Willen auch gegen Widerstreben durchzusetzen, gleichviel worauf diese Chance beruht." Weber sieht Macht als etwas Asymmetrisches und potenziell Repressives – die Fähigkeit, andere zu etwas zu zwingen, was sie sonst nicht täten.</p>
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

    # Card 2: Self-assessment - Herrschaft
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of Max Weber's definition of 'Herrschaft' (domination/authority)",
        "course_task_ref": "le4-ch2-herrschaft",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Herrschaft</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Herrschaft</strong> ist nach Weber „die Chance, für einen Befehl bestimmten Inhalts bei angebbaren Personen Gehorsam zu finden." Im Unterschied zur Macht beruht Herrschaft auf Legitimität – die Beherrschten akzeptieren die Autorität des Herrschenden. Weber unterscheidet drei Typen legitimer Herrschaft: legale, traditionale und charismatische.</p>
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

    # Card 3: Multiple choice - Three types of legitimate rule
    {
        "semantic_description": "Week 5-6: Identify Weber's three types of legitimate authority (Herrschaft)",
        "course_task_ref": "le4-ch2-herrschaftstypen",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Welche drei Typen legitimer Herrschaft unterscheidet Max Weber?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Legale, traditionale und charismatische Herrschaft
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Demokratische, monarchische und diktatorische Herrschaft
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Wirtschaftliche, politische und religiöse Herrschaft
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Militärische, bürokratische und feudale Herrschaft
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

    # Card 4: Self-assessment - Legale Herrschaft
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of 'Legale Herrschaft' (legal-rational authority)",
        "course_task_ref": "le4-ch2-legale-herrschaft",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Legale Herrschaft</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Legale Herrschaft</strong> beruht auf dem Glauben an die Rechtmäßigkeit gesatzter Ordnungen. Die Gehorsamspflicht gilt nicht einer Person, sondern einem unpersönlichen Regelsystem. Der moderne Staat und seine Bürokratie sind typische Beispiele für legale Herrschaft – Beamte handeln nach Gesetzen und Vorschriften, nicht nach persönlicher Willkür.</p>
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

    # Card 5: Self-assessment - Traditionale Herrschaft
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of 'Traditionale Herrschaft' (traditional authority)",
        "course_task_ref": "le4-ch2-traditionale-herrschaft",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Traditionale Herrschaft</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Traditionale Herrschaft</strong> beruht auf dem Glauben an die Heiligkeit überkommener Ordnungen. Gehorsam wird geleistet, weil „es schon immer so war". Beispiele sind das Erbkönigtum oder patriarchale Familienstrukturen. Die Autorität des Herrschers ergibt sich aus Tradition und Gewohnheit, nicht aus rationalen Regeln.</p>
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

    # Card 6: Self-assessment - Charismatische Herrschaft
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of 'Charismatische Herrschaft' (charismatic authority)",
        "course_task_ref": "le4-ch2-charismatische-herrschaft",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Charismatische Herrschaft</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Charismatische Herrschaft</strong> beruht auf der außeralltäglichen Hingabe an die Heiligkeit, Heldenkraft oder Vorbildlichkeit einer Person. Der charismatische Führer wird aufgrund seiner besonderen persönlichen Qualitäten anerkannt. Beispiele sind religiöse Propheten, revolutionäre Führer oder Kriegshelden. Diese Herrschaftsform ist instabil, da sie an die Person gebunden ist.</p>
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

    # =========================================================================
    # Hannah Arendt's Concept of Power
    # =========================================================================

    # Card 7: Self-assessment - Macht (Arendt)
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of Hannah Arendt's contrasting definition of 'Macht' (power)",
        "course_task_ref": "le4-ch2-arendt",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Macht (nach Arendt)</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Macht</strong> ist bei Hannah Arendt grundlegend anders definiert als bei Weber: Sie entsteht durch gemeinsames Handeln und Zusammenwirken von Menschen. Macht ist bei Arendt nicht repressiv, sondern produktiv – sie basiert auf dem Konsens einer Gruppe und dem „Zusammenschluss vieler". Macht ist legitim, wenn sie demokratisch durch Übereinkunft entsteht.</p>
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

    # Card 8: Multiple choice - Weber vs Arendt on Power
    {
        "semantic_description": "Week 5-6: Distinguish between Weber's and Arendt's concepts of power",
        "course_task_ref": "le4-ch2-weber-vs-arendt",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Was ist der Hauptunterschied zwischen Webers und Arendts Machtbegriff?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Weber sieht Macht als Durchsetzung gegen Widerstand; Arendt als gemeinsames Handeln im Konsens
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Weber lehnt Macht ab; Arendt befürwortet sie
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Beide definieren Macht identisch
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Weber schreibt über Politik; Arendt über Philosophie
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

    # Card 9: Multiple choice - Macht vs Gewalt (Arendt)
    {
        "semantic_description": "Week 5-6: Understand Arendt's distinction between power (Macht) and violence (Gewalt)",
        "course_task_ref": "le4-ch2-macht-gewalt",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Wähle die richtige Antwort</p>
        <h2 class="text-lg font-semibold mb-4">Wie unterscheidet Hannah Arendt zwischen Macht und Gewalt?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Macht und Gewalt sind dasselbe
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Macht basiert auf Konsens und gemeinsamem Handeln; Gewalt ist instrumental und zerstört Macht
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Gewalt ist legitimer als Macht
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur der Staat darf Macht ausüben
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

    # Card 10: Free text - Macht vs Herrschaft
    {
        "semantic_description": "Week 5-6: Explain the difference between Weber's concepts of Macht and Herrschaft in own words",
        "course_task_ref": "le4-ch2-comparison",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">LE IV, Kapitel 2: Macht</p>
        <h2 class="text-lg font-semibold mb-4">Erkläre in eigenen Worten: Was ist der Unterschied zwischen Macht und Herrschaft bei Max Weber?</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="5"
                  placeholder="Der Unterschied liegt darin, dass..."></textarea>

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

    # =========================================================================
    # Übung C: Lexicons and Reference Works
    # =========================================================================

    # Card 11: Self-assessment - Fachlexikon
    {
        "semantic_description": "Week 5-6: Self-assess knowledge of 'Fachlexikon' (specialized lexicon) as academic resource",
        "course_task_ref": "ubung-c-vocab",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">Kannst du diesen Begriff erklären?</p>
        <h2 class="text-xl font-bold text-center py-8">Fachlexikon</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Antwort zeigen
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800"><strong>Fachlexikon</strong> (auch: Speziallexikon) ist ein Nachschlagewerk für ein bestimmtes Fachgebiet. Es enthält Definitionen und Erklärungen von Fachbegriffen, verfasst von Expert*innen. Fachlexika sind wichtige Einstiegspunkte für das Verständnis komplexer Konzepte und werden wie Sammelbände zitiert (Artikel als Aufsatz im Sammelband).</p>
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

    # Card 12: Multiple choice - How to cite lexicon articles
    {
        "semantic_description": "Week 5-6: Know how to correctly cite lexicon articles (as essays in edited volume)",
        "course_task_ref": "ubung-c-citation",
        "tags": ["Week 5-6"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Übung C: Korrekte Zitation</p>
        <h2 class="text-lg font-semibold mb-4">Wie werden Lexikonartikel korrekt zitiert?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Als Aufsatz in einem Sammelband (mit Autor, Artikeltitel, Herausgeber, Seitenzahlen)
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Als eigenständige Monographie
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Nur mit dem Lexikontitel, ohne Autor
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Lexikonartikel werden nicht zitiert
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
]

# =============================================================================
# TASK PAGES
# =============================================================================

task_pages = [
    {
        "id": "ubung-c-lexikon-vergleich",
        "title": "Übung C: Lexikon-Vergleich",
        "description": "Vergleiche die Artikel 'Familie' in zwei verschiedenen Soziologie-Lexika und erstelle korrekte Zitationen.",
        "tags": ["Week 5-6"],
        "topics": ["lexikon", "zitation", "sammelband", "familie"],
        "estimated_duration_minutes": 40,
        "difficulty": "beginner",
        "page_html": '''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Übung C: Lexikon-Vergleich</title>
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
<div class="max-w-2xl mx-auto pb-20">
<h1 class="text-2xl font-bold text-gray-800 mb-2">Übung C: Lexikon-Vergleich</h1>
<p class="text-gray-600 text-sm mb-6">Vergleiche zwei Soziologie-Lexika und übe das korrekte Zitieren</p>

<!-- Quick Links -->
<div class="flex gap-3 mb-6">
    <a href="https://www.fernuni-hagen.de/bibliothek/" target="_blank"
       class="flex-1 py-3 bg-green-600 text-white rounded-lg text-center font-medium hover:bg-green-700">
        UB Katalog
    </a>
</div>

<!-- Instructions -->
<div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg mb-6">
    <p class="text-amber-800 text-sm"><strong>Hinweis:</strong> Suche im UB-Katalog nach den beiden Lexika und lies die Artikel zu "Familie", "Mikrosoziologie" und "Kernfamilie".</p>
</div>

<!-- Lexica Info -->
<div class="bg-white rounded-lg shadow-sm p-5 mb-4">
    <h2 class="text-lg font-semibold text-gray-700 mb-3">Die zwei Lexika</h2>
    <ul class="space-y-2 text-sm text-gray-600">
        <li><strong>1.</strong> Klimke et al. (Hrsg.). 2020. <em>Lexikon zur Soziologie</em>. 6. Auflage. Springer VS.</li>
        <li><strong>2.</strong> Reinhold et al. (Hrsg.). 2000. <em>Soziologie-Lexikon</em>. 4. Auflage. Oldenbourg.</li>
    </ul>
</div>

<!-- Task 1: Formal Differences -->
<div class="bg-white rounded-lg shadow-sm p-5 mb-4">
    <h2 class="text-lg font-semibold text-gray-700 mb-3">Aufgabe 1: Formale Unterschiede</h2>
    <p class="text-gray-600 text-sm mb-4">Vergleiche die Artikel "Familie" in beiden Lexika. Notiere die <strong>formalen</strong> (nicht inhaltlichen) Unterschiede.</p>

    <label class="block text-sm font-medium text-gray-700 mb-1">Länge der Artikel:</label>
    <textarea id="q1_length" rows="2" class="w-full p-3 border border-gray-300 rounded-lg mb-3" placeholder="z.B. Der Artikel in Klimke ist... Seiten, während..."></textarea>

    <label class="block text-sm font-medium text-gray-700 mb-1">Nachbarbegriffe:</label>
    <textarea id="q1_neighbors" rows="2" class="w-full p-3 border border-gray-300 rounded-lg mb-3" placeholder="Welche verwandten Begriffe stehen in der Nähe?"></textarea>

    <label class="block text-sm font-medium text-gray-700 mb-1">Literaturhinweise:</label>
    <textarea id="q1_refs" rows="2" class="w-full p-3 border border-gray-300 rounded-lg" placeholder="Wie viele? Wie alt sind sie?"></textarea>
</div>

<!-- Task 2: Literature Analysis -->
<div class="bg-white rounded-lg shadow-sm p-5 mb-4">
    <h2 class="text-lg font-semibold text-gray-700 mb-3">Aufgabe 2: Literatur analysieren</h2>
    <p class="text-gray-600 text-sm mb-4">Was fällt dir bei der zitierten Literatur in den "Familie"-Artikeln auf?</p>
    <textarea id="q2" rows="4" class="w-full p-3 border border-gray-300 rounded-lg" placeholder="Mir fällt auf, dass..."></textarea>
</div>

<!-- Task 3: Citations -->
<div class="bg-white rounded-lg shadow-sm p-5 mb-4">
    <h2 class="text-lg font-semibold text-gray-700 mb-3">Aufgabe 3: Korrekte Zitation</h2>
    <p class="text-gray-600 text-sm mb-4">Bibliographiere beide "Familie"-Artikel korrekt (als Aufsätze im Sammelband).</p>

    <label class="block text-sm font-medium text-gray-700 mb-1">Zitation Klimke et al. (2020):</label>
    <textarea id="q3_klimke" rows="3" class="w-full p-3 border border-gray-300 rounded-lg mb-3" placeholder="[Autor]. 2020. 'Familie.' In..."></textarea>

    <label class="block text-sm font-medium text-gray-700 mb-1">Zitation Reinhold et al. (2000):</label>
    <textarea id="q3_reinhold" rows="3" class="w-full p-3 border border-gray-300 rounded-lg" placeholder="[Autor]. 2000. 'Familie.' In..."></textarea>
</div>

<!-- Action Buttons -->
<div class="flex gap-3 sticky bottom-4">
    <button onclick="saveDraft()" class="flex-1 py-3 bg-amber-100 text-amber-700 rounded-lg font-medium hover:bg-amber-200">
        Entwurf speichern
    </button>
    <button onclick="submitAnswers()" class="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700">
        Abschliessen
    </button>
</div>
<div id="status" class="mt-4 text-center text-sm text-gray-500"></div>
</div>

<script>
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const status = await TaskAPI.getStatus();
        if (status.notes) {
            const saved = JSON.parse(status.notes);
            if (saved.q1_length) document.getElementById('q1_length').value = saved.q1_length;
            if (saved.q1_neighbors) document.getElementById('q1_neighbors').value = saved.q1_neighbors;
            if (saved.q1_refs) document.getElementById('q1_refs').value = saved.q1_refs;
            if (saved.q2) document.getElementById('q2').value = saved.q2;
            if (saved.q3_klimke) document.getElementById('q3_klimke').value = saved.q3_klimke;
            if (saved.q3_reinhold) document.getElementById('q3_reinhold').value = saved.q3_reinhold;
            showStatus('Entwurf wiederhergestellt', 'success');
        }
    } catch (e) {
        console.log('No draft to restore:', e);
    }
});

function getAnswers() {
    return {
        q1_length: document.getElementById('q1_length').value,
        q1_neighbors: document.getElementById('q1_neighbors').value,
        q1_refs: document.getElementById('q1_refs').value,
        q2: document.getElementById('q2').value,
        q3_klimke: document.getElementById('q3_klimke').value,
        q3_reinhold: document.getElementById('q3_reinhold').value
    };
}

async function saveDraft() {
    const answers = getAnswers();
    await TaskAPI.saveDraft(JSON.stringify(answers));
    showStatus('Entwurf gespeichert!', 'success');
}

async function submitAnswers() {
    const answers = getAnswers();
    if (!answers.q3_klimke || !answers.q3_reinhold) {
        showStatus('Bitte beide Zitationen ausfüllen (Aufgabe 3)', 'error');
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
    """Insert all Week 5-6 content into the database."""
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
