"""Semantic + keyword search for shlokas."""

import os
import logging
from models.shloka import SHLOKAS, SHLOKA_LOOKUP, CURATED_TOPICS, TOPIC_INDEX
from config import DATA_DIR

logger = logging.getLogger('gitagpt.search')

# Lazy imports for optional dependencies
try:
    import cohere
    import chromadb
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    logger.warning("chromadb/cohere not installed. Keyword matching only.")


class SemanticSearch:
    """Semantic search using Cohere embeddings and ChromaDB."""

    def __init__(self):
        self.co = None
        self.collection = None
        self._initialized = False

    def _init_lazy(self):
        if self._initialized:
            return True

        if not SEMANTIC_AVAILABLE:
            return False

        api_key = os.environ.get('COHERE_API_KEY')
        if not api_key:
            logger.warning("COHERE_API_KEY not set.")
            return False

        chromadb_path = DATA_DIR / 'chromadb_full'
        if not chromadb_path.exists():
            logger.warning(f"ChromaDB not found at {chromadb_path}")
            return False

        try:
            self.co = cohere.Client(api_key)
            client = chromadb.PersistentClient(path=str(chromadb_path))
            self.collection = client.get_collection("gita_full")
            self._initialized = True
            logger.info(f"Semantic search ready: {self.collection.count()} embeddings")
            return True
        except Exception as e:
            logger.error(f"Semantic search init error: {e}")
            return False

    def search(self, query: str, n_results: int = 3) -> list[str]:
        if not self._init_lazy():
            return []

        try:
            response = self.co.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query",
                truncate="END",
            )
            query_embedding = response.embeddings[0]

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["distances"],
            )

            if results and results['ids']:
                return results['ids'][0]
            return []
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []


_semantic_search = SemanticSearch()

# Topic keywords for keyword fallback
USER_QUERY_TOPICS = {
    'karma': ['काम', 'कर्म', 'करना', 'कर्तव्य', 'जिम्मेदारी', 'duty', 'work', 'action'],
    'dharma': ['धर्म', 'सही', 'गलत', 'न्याय', 'right', 'wrong', 'ethics'],
    'bhakti': ['भक्ति', 'प्रार्थना', 'पूजा', 'भगवान', 'ईश्वर', 'prayer', 'god', 'devotion'],
    'gyan': ['ज्ञान', 'समझ', 'सीखना', 'knowledge', 'wisdom', 'understanding'],
    'atma': ['आत्मा', 'soul', 'spirit', 'self'],
    'mrityu': ['मृत्यु', 'मौत', 'death', 'dying', 'मरना'],
    'krodh': ['गुस्सा', 'क्रोध', 'anger', 'angry', 'irritation'],
    'bhay': ['डर', 'भय', 'घबराहट', 'चिंता', 'fear', 'anxiety', 'worried', 'scared'],
    'shanti': ['शांति', 'peace', 'calm', 'peaceful'],
    'dukh': ['दुख', 'तकलीफ', 'परेशानी', 'sad', 'unhappy', 'suffering', 'pain', 'problem'],
    'sukh': ['खुशी', 'सुख', 'happy', 'happiness', 'joy'],
    'moha': ['लगाव', 'मोह', 'attachment', 'obsession'],
    'tyag': ['त्याग', 'छोड़ना', 'let go', 'renounce', 'sacrifice'],
    'man': ['मन', 'सोच', 'विचार', 'mind', 'thoughts', 'thinking'],
    'parivar': ['परिवार', 'घर', 'बच्चे', 'पति', 'पत्नी', 'माता', 'पिता', 'family', 'parents', 'children'],
    'shraddha': ['विश्वास', 'भरोसा', 'faith', 'trust', 'believe'],
    'dhyan': ['ध्यान', 'meditation', 'focus', 'concentrate'],
}


def detect_topics(query: str) -> list[str]:
    query_lower = query.lower()
    detected = []
    for topic, keywords in USER_QUERY_TOPICS.items():
        for kw in keywords:
            if kw.lower() in query_lower:
                detected.append(topic)
                break
    return detected


def find_relevant_shlokas(query: str, max_results: int = 3) -> list[dict]:
    """Find relevant shlokas: semantic search -> curated topics -> keyword fallback."""
    # Try semantic search first
    shloka_ids = _semantic_search.search(query, n_results=max_results)
    if shloka_ids:
        results = [SHLOKA_LOOKUP[sid] for sid in shloka_ids if sid in SHLOKA_LOOKUP]
        if results:
            logger.info(f"[Semantic] {[s['shloka_id'] for s in results]}")
            return results

    # Fallback: curated topics keyword match
    query_lower = query.lower()
    matched = []
    for topic_id, topic_info in CURATED_TOPICS.items():
        for keyword in topic_info.get('keywords', []):
            if keyword.lower() in query_lower:
                for sid in topic_info.get('best_shlokas', []):
                    if sid in SHLOKA_LOOKUP and sid not in [s['shloka_id'] for s in matched]:
                        matched.append(SHLOKA_LOOKUP[sid])
                        if len(matched) >= max_results:
                            return matched
                break

    if matched:
        return matched[:max_results]

    # Fallback: topic index
    topics = detect_topics(query)
    if not topics:
        universal_ids = ['2.47', '2.14', '6.5', '18.66', '2.22']
        return [SHLOKA_LOOKUP[sid] for sid in universal_ids if sid in SHLOKA_LOOKUP][:max_results]

    shloka_scores = {}
    for topic in topics:
        if topic in TOPIC_INDEX:
            for sid in TOPIC_INDEX[topic]:
                shloka_scores[sid] = shloka_scores.get(sid, 0) + 1

    sorted_shlokas = sorted(shloka_scores.items(), key=lambda x: -x[1])
    result_ids = [sid for sid, _ in sorted_shlokas[:max_results]]
    return [SHLOKA_LOOKUP[sid] for sid in result_ids if sid in SHLOKA_LOOKUP]
