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
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {str(e)}"

# -------- MAIN FUNCTION -------- #
def legal_ai(question):
    if not question.strip():
        return "⚠️ Please enter a question."

    try:
        results = search_law(question, top_k=3)

        if not results:
            return "No relevant law found."

        # -------- CONTEXT -------- #
        context = "\n\n".join([item.get("text", "") for item in results])

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

        # -------- SOURCES -------- #
        sources = []
        for item in results:
            metadata = item.get("metadata", {})
            law = metadata.get("law", "Unknown Law")
            sec = metadata.get("section_number", "N/A")
            sources.append(f"{law} - Section {sec}")

        source_text = "\n".join(list(set([str(s) for s in sources]))) if sources else "No sources available"

        return f"{answer}\n\n📚 Sources:\n{source_text}"

    except Exception as e:
        return f"Error: {str(e)}"

# -------- UI -------- #
with gr.Blocks() as demo:
    gr.Markdown("# ⚖️ Indian Law AI Assistant")
    gr.Markdown("Ask any question about Indian law")

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

# -------- LAUNCH (RENDER READY) -------- #
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    demo.launch(server_name="0.0.0.0", server_port=port, share=True)