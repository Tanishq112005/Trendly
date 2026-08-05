from langchain_groq import ChatGroq
from app.core.config import GROQ_API_KEY

# Centralized LLM instance to be shared across all agents
llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0)
