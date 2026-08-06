import os
import logging
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from pinecone import Pinecone, ServerlessSpec

class SemanticCache:
    def __init__(self):
        self.index_name = "trendly-faq-cache"
        self.pinecone_api_key = os.getenv("VECTOR_DB")
        
        hf_api = os.getenv("HUGGING_FACE")
        if hf_api:
            self.embeddings = HuggingFaceEndpointEmbeddings(
                repo_id="sentence-transformers/all-MiniLM-L6-v2",
                huggingfacehub_api_token=hf_api,
            )
        else:
            raise ValueError(
                "No HUGGING_FACE api key provided for embeddings."
            )

        if not self.pinecone_api_key:
            raise ValueError("No VECTOR_DB api key provided for Pinecone.")

        # Initialize Pinecone
        pc = Pinecone(api_key=self.pinecone_api_key)
        
        # Check if index exists, else create it
        if self.index_name not in pc.list_indexes().names():
            logging.info(f"Creating Pinecone index '{self.index_name}'...")
            pc.create_index(
                name=self.index_name,
                dimension=384,  # all-MiniLM-L6-v2 dimension
                metric='cosine',
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
        # Connect to the index
        self.vector_store = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
            pinecone_api_key=self.pinecone_api_key
        )
        
        logging.info("Connected to Pinecone Vector database successfully!")

    async def check_cache(self, query: str, threshold: float = 0.82) -> str | None:
        try:
            # Pinecone similarity search
            results = await self.vector_store.asimilarity_search_with_score(query, k=1)
            if results:
                doc, score = results[0]
                # Pinecone returns cosine similarity: higher is better
                if score >= threshold:
                    logging.info(f"Semantic Cache HIT: Score {score:.4f} for query '{query}'")
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
