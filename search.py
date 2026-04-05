import numpy as np

# Dummy data (replace with your real embeddings + documents later)
documents = [
    "Section 66 of IT Act deals with computer-related offences.",
    "IPC Section 420 relates to cheating and dishonesty.",
    "Article 21 gives right to life and personal liberty."
]

# Dummy embeddings (just for avoiding crash if real ones not loaded)
embeddings = [np.random.rand(384) for _ in documents]

# -------- SIMILARITY FUNCTION -------- #
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------- SEARCH FUNCTION -------- #
def search_law(query, top_k=3):
    # For now, generate a fake embedding for query
    query_embedding = np.random.rand(384)

    similarities = []
    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((sim, i))

    similarities.sort(reverse=True)

    results = []
    for sim, idx in similarities[:top_k]:
        results.append({
            "text": documents[idx],
            "score": float(sim)
        })

    return results