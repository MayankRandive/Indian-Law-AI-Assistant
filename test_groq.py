import os
from groq import Groq

# -------- LOAD API KEY -------- #
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY is not set")

# -------- INITIALIZE CLIENT -------- #
client = Groq(api_key=api_key)

print("=== Legal AI Test ===")
while True:
    question = input("Enter your question (or type 'exit' to quit): ")
    if question.lower() == "exit":
        break

    try:
        response = client.chat.completions.create(
            model="groq/compound",
            messages=[{"role": "user", "content": question}]
        )
        print("\n🧠 Answer:")
        print(response.choices[0].message.content)
    except Exception as e:
        print("Connection error:", e)