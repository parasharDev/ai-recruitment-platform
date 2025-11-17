# services/embeddings_service.py

from openai import AzureOpenAI
from langchain.embeddings.base import Embeddings
import numpy as np
from functools import lru_cache
import os


azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_KEY"),
    api_version="2024-02-01",
    azure_endpoint="https://kraft-050.openai.azure.com/"
)

#  Helper for direct embedding calls
@lru_cache(maxsize=10000)
def azure_embed_text(text: str):
    """Generate a single embedding vector using Azure OpenAI."""
    if not text.strip():
        return np.zeros(1536).tolist()  # match model dimension
    response = azure_client.embeddings.create(
        input=[text],
        model="text-embedding-3-large"
    )
    return response.data[0].embedding


# LangChain-compatible embedding wrapper (for Chroma)
class AzureTextEmbeddings(Embeddings):
    """LangChain-compatible embedding wrapper for Azure OpenAI."""
    def embed_documents(self, texts):
        return [azure_embed_text(t) for t in texts]

    def embed_query(self, text):
        return azure_embed_text(text)
