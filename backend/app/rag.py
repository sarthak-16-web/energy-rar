from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.utils import chunk_text

groq_client = Groq(api_key=GROQ_API_KEY)

document_store = {
    "chunks": [],
    "vectorizer": None,
    "matrix": None,
}


def clear_store():
    document_store["chunks"] = []
    document_store["vectorizer"] = None
    document_store["matrix"] = None


def ingest_document(text: str):
    clear_store()

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No valid chunks found from the PDF.")

    vectorizer = TfidfVectorizer(stop_words="english")
    matrix = vectorizer.fit_transform(chunks)

    document_store["chunks"] = chunks
    document_store["vectorizer"] = vectorizer
    document_store["matrix"] = matrix


def retrieve_context(query: str, top_k: int = 4) -> str:
    chunks = document_store["chunks"]
    vectorizer = document_store["vectorizer"]
    matrix = document_store["matrix"]

    if not chunks or vectorizer is None or matrix is None:
        return ""

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, matrix).flatten()

    top_indices = scores.argsort()[::-1][:top_k]
    selected_chunks = [chunks[i] for i in top_indices if scores[i] > 0]

    return "\n\n".join(selected_chunks)


def answer_question(question: str) -> str:
    context = retrieve_context(question)

    if not context.strip():
        return "The answer is not available in the uploaded PDF."

    prompt = f"""
You are a PDF question-answering assistant.
Answer ONLY from the provided context.
If the answer is not present in the context, say:
"The answer is not available in the uploaded PDF."

Context:
{context}

Question:
{question}
"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Answer strictly from the uploaded PDF context."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content.strip()
