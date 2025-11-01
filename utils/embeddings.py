import numpy as np
from sentence_transformers import SentenceTransformer

# Loading embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Compute cosine similarity between two vectors
def cosine_similarity(vec1, vec2) -> float:
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


# Convert text into embeddings using SentenceTransformer
def embed_text(text: str):
    return embed_model.encode(text)
