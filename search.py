import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import ollama

# ---------------- CONFIG ---------------- #
MODEL_NAME = "mistral"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3

# ---------------- LOAD MODELS ---------------- #
print("Loading embeddings model...")
model = SentenceTransformer(EMBEDDING_MODEL)

print("Loading law chunks...")
with open("law_chunks_structured.json", "r", encoding="utf-8") as f:
    data = json.load(f)

embeddings = np.load("embeddings.npy")
texts = [item["text"] for item in data]

# ---------------- SIMPLE EXPLAIN ---------------- #
def simple_explain(text):
    sentences = text.split(".")
    return sentences[0] + "." if sentences else text

# ---------------- LAW DETECTION ---------------- #
def detect_law(query):
    q = query.lower()
    if "ipc" in q or "penal code" in q:
        return "IPC"
    elif "bns" in q:
        return "BNS"
    elif "crpc" in q or "fir" in q or "arrest" in q or "bail" in q:
        return "CrPC"
    elif "constitution" in q or "article" in q:
        return "Constitution"
    elif "contract" in q:
        return "Contract Act"
    elif "evidence" in q or "iea" in q:
        return "IEA"
    elif "it act" in q or "information technology" in q:
        return "IT Act"
    elif "motor vehicle" in q or "mva" in q:
        return "Motor Vehicles Act"
    elif "consumer protection" in q or "cpa" in q:
        return "Consumer Protection Act"
    elif "police" in q:
        return "Police Act"
    elif "protection of women" in q or "pwdva" in q:
        return "Protection of Women from Domestic Violence Act"
    return None

# ---------------- PRINT RESULT ---------------- #
def print_result(idx):
    result = texts[idx]
    sec = data[idx]["metadata"].get("section_number", "")
    law = data[idx]["metadata"].get("law", "")

    print("\n📘 RESULT:")
    print(f"Law: {law}")
    print(f"Section: {sec}\n")
    print(result)
    print("\n🧠 SIMPLE EXPLANATION:")
    print(simple_explain(result))

# ---------------- OLLAMA FUNCTION ---------------- #
def ask_ollama(query, context_chunks):
    context_text = "\n\n".join(context_chunks)

    prompt = f"""
You are an expert Indian legal assistant.

Use ONLY the legal context below.
Do NOT make up laws.

If answer not present, say:
"I don't have enough legal information."

---------------------
{context_text}
---------------------

Question: {query}

Answer in simple language:
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )

    if response.messages:
        return response.messages[-1].content
    return "No response from Ollama."

# =========================================================
# 🔥 NEW FUNCTION (FOR YOUR LLM PIPELINE - VERY IMPORTANT)
# =========================================================
def search_law(query, top_k=TOP_K):
    query_lower = query.lower()
    detected_law = detect_law(query)

    results = []

    # ---------------- DIRECT MATCH ---------------- #
    match = re.search(r'(section|article)?\s*(\d+[a-z]*)', query_lower)
    if match:
        query_type = match.group(1)
        number = match.group(2)

        for item in data:
            meta = item["metadata"]
            sec = str(meta.get("section_number", "")).lower()
            law = meta.get("law", "")

            if sec != number:
                continue
            if query_type == "article" and law != "Constitution":
                continue
            if detected_law and law != detected_law:
                continue

            results.append({
                "content": item["text"],
                "metadata": meta
            })

        if results:
            return results[:top_k]

    # ---------------- SEMANTIC SEARCH ---------------- #
    query_embedding = model.encode([query])
    scores = cosine_similarity(query_embedding, embeddings)[0]

    # Law filter
    filtered = []
    for i in range(len(data)):
        law = data[i]["metadata"].get("law", "")
        if detected_law and law != detected_law:
            continue
        filtered.append((i, scores[i]))

    if not filtered:
        return []

    filtered.sort(key=lambda x: x[1], reverse=True)

    for idx, score in filtered[:top_k]:
        item = data[idx]
        results.append({
            "content": item["text"],
            "metadata": item["metadata"]
        })

    return results

# =========================================================
# OLD FUNCTION (UNCHANGED - CLI MODE)
# =========================================================
def search(query):
    query_lower = query.lower()
    detected_law = detect_law(query)

    if "article" in query_lower and detected_law not in [None, "Constitution"]:
        print("\n⚖️ SYSTEM RESPONSE:")
        print("Articles exist only in Constitution.")
        return

    match = re.search(r'(section|article)?\s*(\d+[a-z]*)', query_lower)
    if match:
        query_type = match.group(1)
        number = match.group(2)
        candidates = []

        for i, item in enumerate(data):
            meta = item["metadata"]
            sec = str(meta.get("section_number", "")).lower()
            law = meta.get("law", "")

            if sec != number:
                continue
            if query_type == "article" and law != "Constitution":
                continue
            if detected_law and law != detected_law:
                continue

            candidates.append(i)

        if candidates:
            print("\n📘 DIRECT MATCH:")
            print_result(candidates[0])
            answer = ask_ollama(query, [texts[candidates[0]]])
            print("\n🤖 Ollama Answer:")
            print(answer)
            return

    print("\n⚖️ Try using the new RAG pipeline instead.")

# ---------------- MAIN LOOP ---------------- #
if __name__ == "__main__":
    print("=== Legal Query System ===")
    while True:
        q = input("\nEnter your question (or type 'exit' to quit): ")
        if q.lower() == "exit":
            break
        search(q)