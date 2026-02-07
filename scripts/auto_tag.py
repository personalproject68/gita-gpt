#!/usr/bin/env python3
"""
Auto-tagger for Bhagavad Gita shlokas.
Tags shlokas based on keywords in Hindi meaning and commentary.
"""

import json
from pathlib import Path

# Topic keywords mapping (Hindi keywords -> tag)
TOPIC_KEYWORDS = {
    'karma': [
        'कर्म', 'कर्तव्य', 'काम', 'कार्य', 'क्रिया', 'करना', 'कर्मफल',
        'कर्मयोग', 'निष्काम', 'सकाम'
    ],
    'dharma': [
        'धर्म', 'कर्तव्य', 'न्याय', 'सत्य', 'धर्मात्मा', 'स्वधर्म'
    ],
    'bhakti': [
        'भक्ति', 'भक्त', 'प्रेम', 'श्रद्धा', 'पूजा', 'उपासना', 'भजन',
        'समर्पण', 'शरणागति', 'प्रभु'
    ],
    'gyan': [
        'ज्ञान', 'विद्या', 'बुद्धि', 'विवेक', 'समझ', 'ज्ञानी', 'तत्त्वज्ञान',
        'आत्मज्ञान', 'विचार'
    ],
    'atma': [
        'आत्मा', 'आत्म', 'जीवात्मा', 'परमात्मा', 'अविनाशी', 'नित्य',
        'शाश्वत', 'अमर', 'देही'
    ],
    'mrityu': [
        'मृत्यु', 'मरण', 'मौत', 'देहान्त', 'शरीर त्याग', 'अन्तकाल'
    ],
    'krodh': [
        'क्रोध', 'गुस्सा', 'कोप', 'रोष', 'आक्रोश'
    ],
    'bhay': [
        'भय', 'डर', 'भीत', 'आशंका', 'चिन्ता', 'घबराहट'
    ],
    'shanti': [
        'शान्ति', 'शांति', 'निर्भय', 'स्थिर', 'समाधान', 'चैन', 'सुख'
    ],
    'dukh': [
        'दुःख', 'दुख', 'कष्ट', 'पीड़ा', 'वेदना', 'शोक', 'विषाद'
    ],
    'sukh': [
        'सुख', 'आनन्द', 'प्रसन्नता', 'हर्ष', 'खुशी'
    ],
    'moha': [
        'मोह', 'आसक्ति', 'लगाव', 'ममता', 'अज्ञान'
    ],
    'tyag': [
        'त्याग', 'वैराग्य', 'संन्यास', 'छोड़ना', 'परित्याग'
    ],
    'sansar': [
        'संसार', 'जगत्', 'संसारिक', 'लौकिक', 'माया', 'भवसागर'
    ],
    'man': [
        'मन', 'चित्त', 'मानसिक', 'विचार', 'संकल्प', 'मनःस्थिति'
    ],
    'indriya': [
        'इन्द्रिय', 'विषय', 'संयम', 'जितेन्द्रिय', 'वश'
    ],
    'yuddh': [
        'युद्ध', 'लड़ाई', 'संग्राम', 'रण', 'क्षत्रिय'
    ],
    'paap': [
        'पाप', 'अधर्म', 'दोष', 'अपराध'
    ],
    'punya': [
        'पुण्य', 'शुभ', 'सत्कर्म', 'पवित्र'
    ],
    'guru': [
        'गुरु', 'आचार्य', 'शिक्षक', 'उपदेश'
    ],
    'parivar': [
        'परिवार', 'कुटुम्ब', 'पुत्र', 'पिता', 'माता', 'पत्नी', 'सम्बन्धी',
        'भाई', 'बहन', 'पितामह'
    ],
    'samatva': [
        'समता', 'समभाव', 'समान', 'निःपक्षपात', 'सम'
    ],
    'shraddha': [
        'श्रद्धा', 'विश्वास', 'आस्था', 'निष्ठा'
    ],
    'satvik': [
        'सात्त्विक', 'सत्त्वगुण', 'शुद्ध', 'पवित्र'
    ],
    'rajasik': [
        'राजसिक', 'रजोगुण', 'कामना', 'लालसा'
    ],
    'tamasik': [
        'तामसिक', 'तमोगुण', 'आलस्य', 'प्रमाद', 'अज्ञान'
    ],
    'dhyan': [
        'ध्यान', 'समाधि', 'एकाग्रता', 'योग', 'मनन'
    ],
    'prem': [
        'प्रेम', 'स्नेह', 'प्यार', 'वात्सल्य'
    ],
    'sewa': [
        'सेवा', 'परोपकार', 'दान', 'मदद'
    ],
    'sahas': [
        'साहस', 'वीरता', 'पराक्रम', 'निर्भय', 'हिम्मत', 'बहादुरी'
    ],
    'ahankar': [
        'अहंकार', 'गर्व', 'अभिमान', 'मद', 'घमण्ड'
    ],
    'nishtha': [
        'निष्ठा', 'समर्पण', 'दृढ़ता', 'एकाग्र'
    ]
}

# Famous/important shlokas that should always be tagged
FAMOUS_SHLOKAS = {
    '2.47': ['karma', 'nishkam_karma'],  # कर्मण्येवाधिकारस्ते
    '2.14': ['dukh', 'sukh', 'samatva'],  # मात्रास्पर्शास्तु कौन्तेय
    '2.22': ['atma', 'mrityu'],  # वासांसि जीर्णानि
    '2.27': ['mrityu', 'atma'],  # जातस्य हि ध्रुवो मृत्युः
    '3.35': ['dharma', 'swadharma'],  # स्वधर्मे निधनं श्रेयः
    '4.7': ['dharma', 'avatar'],  # यदा यदा हि धर्मस्य
    '4.8': ['dharma', 'avatar'],  # परित्राणाय साधूनां
    '6.5': ['man', 'atma'],  # उद्धरेदात्मनात्मानं
    '9.22': ['bhakti', 'shraddha'],  # अनन्याश्चिन्तयन्तो माम्
    '11.32': ['mrityu', 'kaal'],  # कालोऽस्मि लोकक्षयकृत्
    '18.66': ['bhakti', 'sharanagati'],  # सर्वधर्मान्परित्यज्य
}


def auto_tag_shloka(shloka: dict) -> list[str]:
    """Auto-tag a shloka based on keywords in its Hindi meaning and commentary."""
    tags = set()

    # Check if it's a famous shloka
    shloka_id = shloka.get('shloka_id', '')
    if shloka_id in FAMOUS_SHLOKAS:
        tags.update(FAMOUS_SHLOKAS[shloka_id])

    # Combine text to search
    text_to_search = ' '.join([
        shloka.get('hindi_meaning', ''),
        shloka.get('hindi_commentary', '')[:500]  # First 500 chars of commentary
    ]).lower()

    # Check for topic keywords
    for tag, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_to_search:
                tags.add(tag)
                break

    return list(tags)


def create_topic_index(shlokas: list[dict]) -> dict:
    """Create an index of topics to shloka IDs for quick lookup."""
    index = {}

    for shloka in shlokas:
        for tag in shloka.get('tags', []):
            if tag not in index:
                index[tag] = []
            index[tag].append(shloka['shloka_id'])

    return index


def main():
    """Main function to auto-tag all shlokas."""
    data_dir = Path(__file__).parent.parent / 'data'

    # Load shlokas
    with open(data_dir / 'gita_complete.json', 'r', encoding='utf-8') as f:
        shlokas = json.load(f)

    print(f"Loaded {len(shlokas)} shlokas")
    print("Auto-tagging...")

    # Auto-tag each shloka
    for shloka in shlokas:
        shloka['tags'] = auto_tag_shloka(shloka)

    # Count tags
    tag_counts = {}
    for shloka in shlokas:
        for tag in shloka['tags']:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print("\nTag distribution:")
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count} shlokas")

    # Save tagged data
    with open(data_dir / 'gita_tagged.json', 'w', encoding='utf-8') as f:
        json.dump(shlokas, f, ensure_ascii=False, indent=2)
    print(f"\nSaved tagged data to {data_dir / 'gita_tagged.json'}")

    # Create and save topic index
    topic_index = create_topic_index(shlokas)
    with open(data_dir / 'topic_index.json', 'w', encoding='utf-8') as f:
        json.dump(topic_index, f, ensure_ascii=False, indent=2)
    print(f"Saved topic index to {data_dir / 'topic_index.json'}")

    # Show sample
    print("\nSample tagged shlokas:")
    for shloka in shlokas[:3]:
        print(f"  {shloka['shloka_id']}: {shloka['tags']}")


if __name__ == '__main__':
    main()
