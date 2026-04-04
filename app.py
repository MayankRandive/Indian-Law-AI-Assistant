from flask import Flask, render_template, request, jsonify
from search import search_law
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# -------- GROQ SETUP -------- #
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)


def ask_llm(prompt):
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


# -------- ROUTES -------- #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    try:
        user_question = request.json.get("question")

        results = search_law(user_question, top_k=3)

        if not results:
            return jsonify({"answer": "No relevant law found."})

        # Use correct key from your search.py
        context = "\n\n".join([item["text"] for item in results])

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

        answer = ask_llm(prompt)

        return jsonify({"answer": answer})

    except Exception as e:
        return jsonify({"answer": f"Error: {str(e)}"})


# -------- RUN APP -------- #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)