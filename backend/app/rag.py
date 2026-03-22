import uuid
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL, CHROMA_DIR, COLLECTION_NAME
from app.utils import chunk_text

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
groq_client = Groq(api_key=GROQ_API_KEY)


def clear_collection():
    global collection

    try:
        chroma_client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def ingest_document(text: str):
    clear_collection()

    chunks = chunk_text(text)

    if not chunks:
        raise ValueError("No valid chunks found from the PDF.")

    embeddings = embedding_model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"source": "uploaded_pdf"} for _ in chunks]
    )


def retrieve_context(query: str, top_k: int = 4) -> str:
    query_embedding = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents)


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
        temperature=0.1
    )

    return response.choices[0].message.content.strip()