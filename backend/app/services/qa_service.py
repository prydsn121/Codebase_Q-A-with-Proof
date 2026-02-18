from app.config import settings
from openai import OpenAI
import re


# ==============================
# 🔹 Prompt Builder (OpenAI Mode)
# ==============================
def build_prompt(question, retrieved_chunks):
    context = ""

    for chunk in retrieved_chunks:
       
            context += f"\n\nFile: {chunk.get('file_path')}\n"
            context += chunk.get("content", "")
       

    prompt = f"""
You are analyzing a software codebase.

Answer the question ONLY using the provided code.
Do not guess.
If the answer is not present, say:
"Not found in provided code."

Be precise:
- Mention exact file paths
- Mention function names
- Be concise

Question:
{question}

Code:
{context}
"""

    return prompt


# ==============================
# 🔹 Main Answer Generator
# ==============================
def generate_answer(question, retrieved_chunks):

    if not retrieved_chunks:
        return "No relevant information found."

    # ==============================
    # 🟢 OpenAI Mode
    # ==============================
    if settings.USE_OPENAI:

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = build_prompt(question, retrieved_chunks)

        response = client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior backend engineer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()

    # ==============================
    # 🔵 Smart Local Mode (Improved)
    # ==============================
    else:

        # 🔥 Clean punctuation
        cleaned_question = re.sub(r"[^\w\s]", "", question.lower())

        # 🔥 Remove useless words
        stop_words = {
            "where", "is", "the", "a", "an",
            "how", "what", "when", "why",
            "does", "do", "are", "handled",
            "in", "of", "to", "for"
        }

        keywords = [
            word for word in cleaned_question.split()
            if word not in stop_words and len(word) > 2
        ]

        explanation = ""

        for chunk in retrieved_chunks:

            if not isinstance(chunk, dict):
                continue

            file_path = chunk.get("file_path")
            content = chunk.get("content", "")

            lines = content.split("\n")

            matched_lines = []

            for line in lines:
                line_lower = line.lower()

                # 🔥 Partial match (auth matches authentication)
                if any(keyword in line_lower for keyword in keywords):
                    matched_lines.append(line.strip())

            if matched_lines:
                explanation += f"\n📄 File: {file_path}\n"
                explanation += "Relevant lines:\n"

                for line in matched_lines[:5]:
                    explanation += f"   • {line}\n"

        if not explanation:
            return "Not found in provided code."

        return explanation.strip()
