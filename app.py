import gradio as gr
from search import search_law
from groq import Groq
import os

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


# -------- MAIN FUNCTION -------- #
def legal_ai(question):
    try:
        results = search_law(question, top_k=3)

        if not results:
            return "No relevant law found."

        context = "\n\n".join([item["text"] for item in results])

        prompt = f"""
You are an expert Indian legal assistant.

Use ONLY the legal context below.
Do NOT make up laws.

---------------------
{context}
---------------------

Question: {question}

Answer in simple language:
"""

        answer = ask_llm(prompt)
        return answer

    except Exception as e:
        return f"Error: {str(e)}"


# -------- GRADIO UI -------- #
iface = gr.Interface(
    fn=legal_ai,
    inputs=gr.Textbox(lines=2, placeholder="Ask about Indian law..."),
    outputs="text",
    title="⚖️ Indian Law AI Assistant",
    description="Ask any question about Indian law"
)

iface.launch()