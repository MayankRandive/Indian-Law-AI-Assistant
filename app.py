from flask import Flask, render_template, request, jsonify
from search import search_law
import requests

app = Flask(__name__)

# -------- OLLAMA -------- #
def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "mistral",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

# -------- ROUTES -------- #

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question")

    results = search_law(user_question, top_k=3)

    if not results:
        return jsonify({"answer": "No relevant law found."})

    context = "\n\n".join([item["content"] for item in results])

    prompt = f"""
You are an expert Indian legal assistant.

Use ONLY the legal context below.
Do NOT make up laws.

---------------------
{context}
---------------------

Question: {user_question}

Answer in simple language:
"""

    answer = ask_ollama(prompt)

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)