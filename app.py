import gradio as gr
from search import search_law
from groq import Groq
import os

# -------- GROQ SETUP -------- #
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

client = Groq(api_key=api_key)

# -------- LLM CALL -------- #
def ask_llm(prompt):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # best available model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500
    )
    return response.choices[0].message.content

# -------- MAIN FUNCTION -------- #
def legal_ai(question):
    try:
        results = search_law(question, top_k=3)

        if not results:
            return "No relevant law found."

        # Context for LLM
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

        if not answer:
            answer = "No response from LLM."

        # 🔥 Add source info (very important upgrade)
        sources = []
        for item in results:
            law = item["metadata"].get("law", "Unknown Law")
            sec = item["metadata"].get("section_number", "N/A")
            sources.append(f"{law} - Section {sec}")

        source_text = "\n".join(set(sources))

        return f"{answer}\n\n📚 Sources:\n{source_text}"

    except Exception as e:
        return f"Error: {str(e)}"

# -------- UI (CLEAN + MODERN) -------- #
with gr.Blocks() as demo:
    gr.Markdown("# ⚖️ Indian Law AI Assistant")
    gr.Markdown("Ask any question about Indian law")

    with gr.Row():
        question_input = gr.Textbox(
            placeholder="Ask about Indian law...",
            lines=3,
            label="Your Question"
        )

    submit_btn = gr.Button("Ask")

    answer_output = gr.Textbox(
        label="Answer",
        lines=12
    )

    # Button + Enter support
    submit_btn.click(
        legal_ai,
        inputs=question_input,
        outputs=answer_output
    )

    question_input.submit(
        legal_ai,
        inputs=question_input,
        outputs=answer_output
    )

# -------- LAUNCH -------- #
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=10000)