from flask import Flask, render_template, request, jsonify
from search import search_law
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# -------- GROQ SETUP -------- #
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

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
    user_question = request.json.get("question")

    results = search_law(user_question, top_k=3)

    if not results:
        return jsonify({"answer": "No relevant law found."})

    # NOTE: your search returns "text", not "content"
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


# -------- RUN APP -------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)