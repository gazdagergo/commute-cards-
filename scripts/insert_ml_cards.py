#!/usr/bin/env python3
"""
Insert ML learning cards (hello-world-model) into the database.

Usage:
    python scripts/insert_ml_cards.py | fly postgres connect -a sociology-pwa-db -d sociology_learning_pwa

See CARD_CONVENTION.md and docs/CARD-CREATION-GUIDE.md for card creation guidelines.
"""

import json

# Default tag for all ML cards
DEFAULT_TAGS = ["ML Basics"]

cards = [
    # Card 1: Self-assessment - Why convert text to numbers
    {
        "semantic_description": "ML Basics Step 1: Understand why computers need text converted to numbers",
        "course_task_ref": "ml-step1",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">ML Fundamentals</p>
        <h2 class="text-xl font-bold text-center py-8">Why must text be converted to numbers before ML processing?</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Show Answer
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800">Computers fundamentally only work with numbers - they cannot process text directly. All operations in a computer (including neural network calculations like dot products and matrix multiplications) are mathematical operations that require numerical inputs. Converting text to numbers is the essential first step in any ML pipeline.</p>
            </div>

            <p class="text-center text-sm text-gray-600">How well did you know this?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Not at all</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Partially</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Well</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Continue</span>
                <span x-show="submitting">Sending...</span>
            </button>
        </div>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 2: Multiple choice - One-hot encoding purpose
    {
        "semantic_description": "ML Basics Step 2: Understand why one-hot encoding is needed instead of plain numbers",
        "course_task_ref": "ml-step2",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Choose the correct answer</p>
        <h2 class="text-lg font-semibold mb-4">Why do we use one-hot encoding instead of plain numbers (like ASCII codes) for characters?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                Plain numbers create false mathematical relationships (e.g., 'l' seems "bigger" than 'e')
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                One-hot encoding uses less memory
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                ASCII codes are too slow to compute
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                One-hot encoding only works with English text
            </button>
        </div>

        <button @click="submitResponse({ selected_index: selected, correct_index: 0 })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Confirm</span>
            <span x-show="submitting">Sending...</span>
        </button>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card 3: Self-assessment - One-hot vector
    {
        "semantic_description": "ML Basics Step 2: Understand one-hot vector structure",
        "course_task_ref": "ml-step2",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">ML Fundamentals</p>
        <h2 class="text-xl font-bold text-center py-8">One-Hot Vector</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Show Answer
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800 mb-2">A <strong>one-hot vector</strong> represents a category as a vector of 0s with exactly one 1 ("hot") at the position corresponding to that category.</p>
                <p class="text-gray-700 text-sm font-mono mt-2">Example with vocab [h,e,l,o]:<br/>
                h = [1,0,0,0]<br/>
                e = [0,1,0,0]<br/>
                l = [0,0,1,0]<br/>
                o = [0,0,0,1]</p>
                <p class="text-gray-600 text-sm mt-2">This makes each category "equally different" from all others.</p>
            </div>

            <p class="text-center text-sm text-gray-600">How well did you know this?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Not at all</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Partially</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Well</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Continue</span>
                <span x-show="submitting">Sending...</span>
            </button>
        </div>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 4: Fill-in-blank - Dot product formula
    {
        "semantic_description": "ML Basics Step 3: Understand dot product calculation",
        "course_task_ref": "ml-step3",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Fill in the missing number</p>

        <p class="text-lg mb-4">
            Given vectors A = [2, 3, 1] and B = [1, 2, 3], the dot product A · B equals:<br/><br/>
            (2×1) + (3×2) + (1×3) = 2 + 6 + 3 = _______
        </p>

        <input type="text" x-model="answer"
               class="w-full p-3 border border-gray-300 rounded-lg text-center text-lg focus:ring-2 focus:ring-indigo-500"
               placeholder="Enter number">

        <button @click="submitResponse({ blank_answer: answer.trim(), expected: '11' })"
                :disabled="submitting || answer.trim() === ''"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Check</span>
            <span x-show="submitting">Sending...</span>
        </button>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"blank_answer": {"type": "string"}, "expected": {"type": "string"}}, "required": ["blank_answer"]}
    },

    # Card 5: Self-assessment - Dot product
    {
        "semantic_description": "ML Basics Step 3: Understand what dot product measures",
        "course_task_ref": "ml-step3",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">ML Fundamentals</p>
        <h2 class="text-xl font-bold text-center py-8">What does the dot product measure?</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Show Answer
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800">The dot product measures <strong>similarity or alignment</strong> between two vectors:</p>
                <ul class="list-disc list-inside mt-2 text-gray-700 text-sm">
                    <li><strong>High positive</strong> → vectors point in similar directions</li>
                    <li><strong>Zero</strong> → vectors are perpendicular (unrelated)</li>
                    <li><strong>Negative</strong> → vectors point in opposite directions</li>
                </ul>
                <p class="text-gray-600 text-sm mt-2">In neural networks, it combines inputs with weights to produce the neuron's output.</p>
            </div>

            <p class="text-center text-sm text-gray-600">How well did you know this?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Not at all</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Partially</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Well</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Continue</span>
                <span x-show="submitting">Sending...</span>
            </button>
        </div>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 6: Multiple choice - Why activation functions
    {
        "semantic_description": "ML Basics Step 4: Understand why activation functions are needed",
        "course_task_ref": "ml-step4",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Choose the correct answer</p>
        <h2 class="text-lg font-semibold mb-4">Why are activation functions essential in neural networks?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                They make computations faster
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                They add non-linearity, allowing networks to learn complex patterns
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                They reduce the number of weights needed
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                They are only used for visualization
            </button>
        </div>

        <button @click="submitResponse({ selected_index: selected, correct_index: 1 })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Confirm</span>
            <span x-show="submitting">Sending...</span>
        </button>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card 7: Self-assessment - ReLU
    {
        "semantic_description": "ML Basics Step 4: Understand ReLU activation function",
        "course_task_ref": "ml-step4",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ revealed: false, rating: null }">
        <p class="text-gray-600 text-sm mb-2">ML Fundamentals</p>
        <h2 class="text-xl font-bold text-center py-8">ReLU (Rectified Linear Unit)</h2>

        <button x-show="!revealed"
                @click="revealed = true"
                class="w-full py-3 bg-gray-100 rounded-lg font-medium">
            Show Answer
        </button>

        <div x-show="revealed" x-cloak class="space-y-4">
            <div class="p-4 bg-gray-50 rounded-lg">
                <p class="text-gray-800 mb-2"><strong>ReLU</strong> is the most popular activation function:</p>
                <p class="font-mono text-center text-lg my-2">f(x) = max(0, x)</p>
                <p class="text-gray-700 text-sm">If x > 0: output = x<br/>If x ≤ 0: output = 0</p>
                <p class="text-gray-600 text-sm mt-2"><strong>Why popular?</strong> Simple, fast, and works great in practice. It's the default choice for hidden layers.</p>
            </div>

            <p class="text-center text-sm text-gray-600">How well did you know this?</p>

            <div class="flex gap-2">
                <button @click="rating = 1"
                        :class="rating === 1 ? 'bg-red-600 text-white' : 'bg-red-100 text-red-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Not at all</button>
                <button @click="rating = 2"
                        :class="rating === 2 ? 'bg-yellow-600 text-white' : 'bg-yellow-100 text-yellow-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Partially</button>
                <button @click="rating = 3"
                        :class="rating === 3 ? 'bg-green-600 text-white' : 'bg-green-100 text-green-800'"
                        class="flex-1 py-2 rounded-lg text-sm">Well</button>
            </div>

            <button @click="submitResponse({ self_rating: rating })"
                    :disabled="submitting || rating === null"
                    class="w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
                <span x-show="!submitting">Continue</span>
                <span x-show="submitting">Sending...</span>
            </button>
        </div>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"self_rating": {"type": "integer", "minimum": 1, "maximum": 3}}, "required": ["self_rating"]}
    },

    # Card 8: Fill-in-blank - ReLU output
    {
        "semantic_description": "ML Basics Step 4: Calculate ReLU activation output",
        "course_task_ref": "ml-step4",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Fill in the missing value</p>

        <p class="text-lg mb-4">
            ReLU(x) = max(0, x)<br/><br/>
            What is ReLU(-5)?<br/>
            Answer: _______
        </p>

        <input type="text" x-model="answer"
               class="w-full p-3 border border-gray-300 rounded-lg text-center text-lg focus:ring-2 focus:ring-indigo-500"
               placeholder="Enter number">

        <p class="text-sm text-gray-500 mt-2 text-center">Hint: What's max(0, -5)?</p>

        <button @click="submitResponse({ blank_answer: answer.trim(), expected: '0' })"
                :disabled="submitting || answer.trim() === ''"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Check</span>
            <span x-show="submitting">Sending...</span>
        </button>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"blank_answer": {"type": "string"}, "expected": {"type": "string"}}, "required": ["blank_answer"]}
    },

    # Card 9: Multiple choice - Softmax use case
    {
        "semantic_description": "ML Basics Step 4: Understand when to use Softmax activation",
        "course_task_ref": "ml-step4",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ selected: null }">
        <p class="text-gray-600 text-sm mb-2">Choose the correct answer</p>
        <h2 class="text-lg font-semibold mb-4">When would you use the Softmax activation function?</h2>

        <div class="space-y-2">
            <button @click="selected = 0"
                    :class="selected === 0 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                In hidden layers to speed up training
            </button>
            <button @click="selected = 1"
                    :class="selected === 1 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                In the output layer for multi-class classification (outputs sum to 1.0)
            </button>
            <button @click="selected = 2"
                    :class="selected === 2 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                To convert text to numbers
            </button>
            <button @click="selected = 3"
                    :class="selected === 3 ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'"
                    class="w-full p-3 text-left border rounded-lg transition-colors">
                To reduce memory usage
            </button>
        </div>

        <button @click="submitResponse({ selected_index: selected, correct_index: 1 })"
                :disabled="submitting || selected === null"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50">
            <span x-show="!submitting">Confirm</span>
            <span x-show="submitting">Sending...</span>
        </button>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"selected_index": {"type": "integer"}, "correct_index": {"type": "integer"}}, "required": ["selected_index"]}
    },

    # Card 10: Free text - Complete neuron formula
    {
        "semantic_description": "ML Basics: Explain the complete neuron computation formula",
        "course_task_ref": "ml-step4",
        "tags": ["ML Basics"],
        "card_html": '''<div x-data="cardResponse()" class="p-4">
    <div x-data="{ answer: '' }">
        <p class="text-gray-600 text-sm mb-2">Learning goal: Understand complete neuron computation</p>
        <h2 class="text-lg font-semibold mb-4">In your own words, explain what happens in a single neuron: from receiving inputs to producing an output. Mention the key steps.</h2>

        <textarea x-model="answer"
                  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  rows="5"
                  placeholder="Think about: input vector, weights, dot product, activation..."></textarea>

        <button @click="submitResponse({ answer })"
                :disabled="submitting || answer.trim().length < 20"
                class="mt-4 w-full py-3 bg-indigo-600 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed">
            <span x-show="!submitting">Submit Answer</span>
            <span x-show="submitting">Sending...</span>
        </button>

        <p x-show="error" x-text="error" class="text-red-600 mt-2 text-sm"></p>
    </div>
</div>''',
        "response_schema": {"type": "object", "properties": {"answer": {"type": "string"}}, "required": ["answer"]}
    },
]


def generate_sql():
    """Generate SQL INSERT statements for the cards."""
    sql_statements = []
    for card in cards:
        # Escape single quotes for SQL
        desc_escaped = card["semantic_description"].replace("'", "''")
        ref_escaped = card["course_task_ref"].replace("'", "''")
        html_escaped = card["card_html"].replace("'", "''")
        schema_json = json.dumps(card["response_schema"]).replace("'", "''")
        tags = card.get("tags", DEFAULT_TAGS)
        tags_sql = "ARRAY[" + ", ".join(f"'{t}'" for t in tags) + "]"

        sql = f"""INSERT INTO cards (semantic_description, course_task_ref, card_html, response_schema, visibility, card_type, tags)
VALUES (
    '{desc_escaped}',
    '{ref_escaped}',
    '{html_escaped}',
    '{schema_json}'::jsonb,
    'public',
    'learning',
    {tags_sql}
);"""
        sql_statements.append(sql)

    return "\n\n".join(sql_statements)


if __name__ == "__main__":
    print("-- ML Hello World Model Cards")
    print(f"-- Generated {len(cards)} cards\n")
    print(generate_sql())
