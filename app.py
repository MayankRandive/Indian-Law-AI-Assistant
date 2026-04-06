from flask import Flask, render_template, request, jsonify
from search import search_law
import requests

app = Flask(__name__)

# -------- OLLAMA -------- #
def ask_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "No response from model.")
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"


# -------- QUERY FILTER -------- #
def is_legal_query(query):
    query = query.lower()

    legal_keywords = [
        "section", "ipc", "crpc", "bns", "law", "act",
        "article", "legal", "court", "police",
        "arrest", "bail", "crime", "fir"
    ]

    problem_keywords = [
        "stolen", "theft", "robbed", "fraud", "scam",
        "harassment", "assault", "cheated", "threat",
        "kidnap", "murder", "violence", "abuse",
        "lost phone", "stole", "cybercrime"
    ]

    return any(k in query for k in legal_keywords + problem_keywords)


# -------- ROUTES -------- #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").strip()

    if not user_question:
        return jsonify({"answer": "⚠️ Please enter a question."})

    # -------- NON-LEGAL HANDLING -------- #
    if not is_legal_query(user_question):
        return jsonify({
            "answer": "🙂 Hey! I'm a Legal AI Assistant.\n\nPlease ask questions related to Indian law (IPC, CrPC, etc.)."
        })

    # -------- SEARCH -------- #
    results = search_law(user_question, top_k=3)

    if not results:
        return jsonify({"answer": "⚠️ No relevant law found for your query."})

    # -------- CONTEXT -------- #
    context = "\n\n".join([item["content"] for item in results])

    # -------- PROMPT -------- #
    prompt = f"""
You are an expert Indian legal assistant.

If user describes a problem:
- Explain the relevant law
- Tell what action they should take (FIR, police, etc.)

Use ONLY the legal context below.

---------------------
{context}
---------------------

User Problem: {user_question}

Answer in simple language:
"""

    # -------- LLM CALL -------- #
    answer = ask_ollama(prompt)

    return jsonify({"answer": answer})


# -------- RUN -------- #
if __name__ == "__main__":
    app.run(debug=True)