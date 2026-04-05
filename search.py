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
    """Send prompt to Groq LLM and return response."""
    response = client.chat.completions.create(
        model="groq/compound",  # Using your working model
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
            return "No response from LLM."
        return answer
    except Exception as e:
        return f"Error: {str(e)}"

# -------- CLASSIC BLOCKS UI -------- #
with gr.Blocks() as demo:
    gr.Markdown("# ⚖️ Indian Law AI Assistant")
    gr.Markdown("Ask any question about Indian law")

    question_input = gr.Textbox(
        placeholder="Ask about Indian law...",
        lines=4
    )
    answer_output = gr.Textbox()

    # Link input to output
    question_input.submit(
        legal_ai,
        inputs=question_input,
        outputs=answer_output
    )

if __name__ == "__main__":
    # Use localhost classic UI
    demo.launch(server_name="127.0.0.1", server_port=7860)