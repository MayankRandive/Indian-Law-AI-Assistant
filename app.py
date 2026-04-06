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
    keywords = [
        "section", "ipc", "crpc", "bns", "law", "act",
        "article", "legal", "court", "police",
        "arrest", "bail", "crime", "fir"
    ]
    return any(k in query.lower() for k in keywords)


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

Rules:
- Answer ONLY using the legal context below
- Do NOT make up laws
- If answer is not in context, say:
  "I don't have enough legal information."

---------------------
{context}
---------------------

Question: {user_question}

Answer in simple language:
"""

    # -------- LLM CALL -------- #
    answer = ask_ollama(prompt)

    return jsonify({"answer": answer})


# -------- RUN -------- #
if __name__ == "__main__":
    app.run(debug=True)