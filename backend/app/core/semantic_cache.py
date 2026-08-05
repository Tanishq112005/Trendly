import os
import logging
from langchain_redis import RedisVectorStore
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_huggingface import HuggingFaceEndpointEmbeddings

class SemanticCache:
    def __init__(self):
        self.index_name = "trendly_faq_cache"
        self.redis_url = os.getenv("REDIS_URI", "redis://localhost:6379/0")

        # Determine embedding model based on available keys
        nomic_api = os.getenv("NOMIC_API")
        hf_api = os.getenv("HUGGING_FACE")

        if nomic_api:
            self.embeddings = NomicEmbeddings(
                model="nomic-embed-text-v1.5", nomic_api_key=nomic_api
            )
        elif hf_api:
            self.embeddings = HuggingFaceEndpointEmbeddings(
                repo_id="sentence-transformers/all-MiniLM-L6-v2",
                huggingfacehub_api_token=hf_api,
            )
        else:
            raise ValueError(
                "No NOMIC_API or HUGGING_FACE api key provided for embeddings."
            )

        self.vector_store = RedisVectorStore(
            redis_url=self.redis_url,
            index_name=self.index_name,
            embeddings=self.embeddings,
        )
        logging.info("Connected to Redis Vector database successfully!")

    async def check_cache(self, query: str, threshold: float = 0.82) -> str | None:
        try:
            results = await self.vector_store.asimilarity_search_with_score(query, k=1)
            if results:
                doc, score = results[0]
                # Redis Langchain integration returns distances by default in most cases.
                if score < (1.0 - threshold):
                    logging.info(f"Semantic Cache HIT: Distance {score:.4f} for query '{query}'")
                    return doc.metadata.get("response")

            logging.info(f"Semantic Cache MISS for query '{query}'")
            return None
        except Exception as e:
            logging.error(f"Error checking semantic cache: {e}")
            return None

    async def store_cache(self, query: str, response: str):
        try:
            await self.vector_store.aadd_texts(
                texts=[query], metadatas=[{"response": response}]
            )
            logging.info(f"Stored query in semantic cache: '{query}'")
        except Exception as e:
            logging.error(f"Error storing in semantic cache: {e}")

try:
    semantic_cache = SemanticCache()
except Exception as e:
    logging.error(f"Failed to initialize SemanticCache: {e}")
    semantic_cache = None
