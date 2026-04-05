import numpy as np
import json
import os
from sentence_transformers import SentenceTransformer

# -------- LOAD MODEL -------- #
model = SentenceTransformer("all-MiniLM-L6-v2")

# -------- FILE PATHS -------- #
EMBEDDINGS_PATH = "embeddings.npy"
DOCUMENTS_PATH = "law_chunks_structured.json"

# -------- LOAD FILES -------- #
if not os.path.exists(EMBEDDINGS_PATH):
    raise ValueError("embeddings.npy not found")

if not os.path.exists(DOCUMENTS_PATH):
    raise ValueError("law_chunks_structured.json not found")

embeddings = np.load(EMBEDDINGS_PATH)

with open(DOCUMENTS_PATH, "r", encoding="utf-8") as f:
    documents = json.load(f)

# -------- SAFETY CHECK -------- #
if len(embeddings) != len(documents):
    raise ValueError("Mismatch between embeddings and documents length")

# -------- SIMILARITY -------- #
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------- SEARCH FUNCTION -------- #
def search_law(query, top_k=3):
    # ✅ REAL embedding now
    query_embedding = model.encode(query)

    similarities = []

    for i, emb in enumerate(embeddings):
        sim = cosine_similarity(query_embedding, emb)
        similarities.append((sim, i))

    similarities.sort(reverse=True)

    results = []
    for sim, idx in similarities[:top_k]:
        doc = documents[idx]

        results.append({
            "text": doc.get("text", ""),
            "score": float(sim),
            "metadata": {
                "law": doc.get("law", "Unknown Law"),
                "section_number": doc.get("section_number", "N/A")
            }
        })

    return results