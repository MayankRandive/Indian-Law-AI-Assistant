import numpy as np
import os
import pickle

# -------- LOAD DATA -------- #
# Make sure these files exist in your repo
EMBEDDINGS_PATH = "embeddings.pkl"
DOCUMENTS_PATH = "documents.pkl"

if not os.path.exists(EMBEDDINGS_PATH) or not os.path.exists(DOCUMENTS_PATH):
    raise ValueError("Embeddings or documents file not found")

with open(EMBEDDINGS_PATH, "rb") as f:
    embeddings = pickle.load(f)

with open(DOCUMENTS_PATH, "rb") as f:
    documents = pickle.load(f)

# -------- SIMILARITY FUNCTION -------- #
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------- SEARCH FUNCTION -------- #
def search_law(query_embedding, top_k=3):
    similarities = []

    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((sim, i))

    # Sort by similarity (highest first)
    similarities.sort(reverse=True)

    results = []
    for sim, idx in similarities[:top_k]:
        results.append({
            "text": documents[idx],
            "score": float(sim)
        })

    return results