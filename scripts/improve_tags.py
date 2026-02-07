#!/usr/bin/env python3
"""
Improve shloka tagging with more specific topic assignments.
This creates a curated mapping of topics to the most relevant shlokas.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / 'data'

# Manually curated best shlokas for each topic
# These are the most impactful, easy-to-understand shlokas for each life situation
CURATED_TOPICS = {
    'bhay_dar': {  # Fear and anxiety
        'name_hi': 'भय और चिंता',
        'name_en': 'Fear and Anxiety',
        'best_shlokas': ['2.14', '2.15', '2.56', '4.10', '6.35', '18.30'],
        'keywords': ['डर', 'भय', 'चिंता', 'घबराहट', 'anxiety', 'fear', 'worried']
    },
    'krodh_gussa': {  # Anger
        'name_hi': 'क्रोध और गुस्सा',
        'name_en': 'Anger',
        'best_shlokas': ['2.62', '2.63', '3.37', '5.26', '16.21'],
        'keywords': ['गुस्सा', 'क्रोध', 'anger', 'angry', 'irritation']
    },
    'dukh_pareshani': {  # Suffering and problems
        'name_hi': 'दुख और परेशानी',
        'name_en': 'Suffering and Problems',
        'best_shlokas': ['2.14', '2.15', '5.20', '5.21', '6.20', '6.21', '6.22'],
        'keywords': ['दुख', 'तकलीफ', 'परेशानी', 'sad', 'suffering', 'problem', 'difficulty']
    },
    'man_shanti': {  # Peace of mind
        'name_hi': 'मन की शांति',
        'name_en': 'Peace of Mind',
        'best_shlokas': ['2.64', '2.65', '2.66', '2.70', '2.71', '6.7', '5.29'],
        'keywords': ['शांति', 'मन', 'peace', 'calm', 'restless', 'peaceful']
    },
    'karma_kartavya': {  # Duty and action
        'name_hi': 'कर्म और कर्तव्य',
        'name_en': 'Duty and Action',
        'best_shlokas': ['2.47', '2.48', '3.8', '3.19', '4.18', '18.45', '18.46'],
        'keywords': ['कर्म', 'कर्तव्य', 'काम', 'duty', 'work', 'action', 'responsibility']
    },
    'mrityu_loss': {  # Death and loss
        'name_hi': 'मृत्यु और वियोग',
        'name_en': 'Death and Loss',
        'best_shlokas': ['2.11', '2.13', '2.20', '2.22', '2.25', '2.27', '8.5', '8.6'],
        'keywords': ['मृत्यु', 'मौत', 'death', 'loss', 'died', 'मरना']
    },
    'parivar_rishte': {  # Family relationships
        'name_hi': 'परिवार और रिश्ते',
        'name_en': 'Family and Relationships',
        'best_shlokas': ['1.28', '1.31', '2.7', '3.21', '9.29', '12.13', '12.14'],
        'keywords': ['परिवार', 'रिश्ता', 'बच्चे', 'पति', 'पत्नी', 'family', 'relationship']
    },
    'sanshay_confusion': {  # Doubt and confusion
        'name_hi': 'संशय और भ्रम',
        'name_en': 'Doubt and Confusion',
        'best_shlokas': ['2.7', '4.35', '4.39', '4.40', '4.41', '18.63'],
        'keywords': ['संशय', 'भ्रम', 'confusion', 'doubt', 'confused', 'समझ नहीं']
    },
    'dhyan_focus': {  # Meditation and focus
        'name_hi': 'ध्यान और एकाग्रता',
        'name_en': 'Meditation and Focus',
        'best_shlokas': ['6.10', '6.11', '6.12', '6.13', '6.14', '6.25', '6.26'],
        'keywords': ['ध्यान', 'meditation', 'focus', 'concentrate', 'एकाग्रता']
    },
    'bhakti_shraddha': {  # Devotion and faith
        'name_hi': 'भक्ति और श्रद्धा',
        'name_en': 'Devotion and Faith',
        'best_shlokas': ['9.22', '9.26', '9.27', '9.29', '9.34', '12.6', '12.7', '18.65', '18.66'],
        'keywords': ['भक्ति', 'श्रद्धा', 'विश्वास', 'भगवान', 'devotion', 'faith', 'god']
    },
    'ahankar_ego': {  # Ego and pride
        'name_hi': 'अहंकार और घमंड',
        'name_en': 'Ego and Pride',
        'best_shlokas': ['3.27', '5.8', '5.9', '13.8', '16.4', '18.17', '18.26'],
        'keywords': ['अहंकार', 'घमंड', 'ego', 'pride', 'arrogance']
    },
    'tyag_detachment': {  # Renunciation and letting go
        'name_hi': 'त्याग और वैराग्य',
        'name_en': 'Detachment',
        'best_shlokas': ['2.47', '2.48', '5.10', '5.11', '12.16', '12.17', '18.49'],
        'keywords': ['त्याग', 'वैराग्य', 'छोड़ना', 'detachment', 'let go', 'attachment']
    },
    'himmat_courage': {  # Courage and bravery
        'name_hi': 'हिम्मत और साहस',
        'name_en': 'Courage',
        'best_shlokas': ['2.3', '2.31', '2.32', '2.33', '2.37', '2.38', '11.33'],
        'keywords': ['हिम्मत', 'साहस', 'courage', 'brave', 'bravery', 'coward']
    },
    'sukh_happiness': {  # Happiness
        'name_hi': 'सुख और आनंद',
        'name_en': 'Happiness',
        'best_shlokas': ['2.55', '2.66', '5.21', '5.24', '6.27', '6.28', '14.27'],
        'keywords': ['सुख', 'खुशी', 'आनंद', 'happy', 'happiness', 'joy']
    },
    'gyan_wisdom': {  # Knowledge and wisdom
        'name_hi': 'ज्ञान और विवेक',
        'name_en': 'Knowledge and Wisdom',
        'best_shlokas': ['4.33', '4.34', '4.35', '4.36', '4.37', '4.38', '5.16'],
        'keywords': ['ज्ञान', 'विवेक', 'समझ', 'knowledge', 'wisdom', 'understand']
    },
}

def create_curated_index():
    """Create curated topic index."""
    # Save curated topics
    with open(DATA_DIR / 'curated_topics.json', 'w', encoding='utf-8') as f:
        json.dump(CURATED_TOPICS, f, ensure_ascii=False, indent=2)

    print(f"Created curated topics index with {len(CURATED_TOPICS)} topics")

    # Print summary
    print("\nTopics and their best shlokas:")
    for topic_id, info in CURATED_TOPICS.items():
        print(f"  {info['name_hi']} ({info['name_en']}): {info['best_shlokas'][:3]}...")

if __name__ == '__main__':
    create_curated_index()
