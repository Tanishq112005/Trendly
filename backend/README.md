# Trendly Agentic Support Assistant

An autonomous AI agent built for Trendly to handle customer support inquiries, track orders, process policy queries, and intelligently escalate tickets to humans. 

## Tech Stack
- **Framework:** FastAPI, LangGraph, LangChain
- **LLM:** Groq (Llama-3)
- **Vector Store:** Redis / Aiven Valkey (for Semantic Caching of FAQs)
- **Database:** MongoDB (for Ticket Management)

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key
MONGODB_URI=your_mongo_uri
REDIS_URI=your_redis_uri
HUGGING_FACE=your_hf_token
```

### 3. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Run the API Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Your chat endpoint is available at `POST http://127.0.0.1:8000/api/chat/`.

### 5. Running Tests
You can run the end-to-end test suite included in the repository:
```bash
python test_e2e.py
```

## AI-Usage Note
This project was built with the assistance of advanced LLMs (Claude/GPT) for:
- Writing boilerplate FastAPI routes and Pydantic schemas.
- Refactoring the LangGraph multi-agent architecture (splitting monolithic agents into smaller specialized nodes).
- Debugging edge cases like Pydantic AttributeErrors and Groq tool-calling JSON parsing failures.
- Designing the Semantic Caching layer with LangChain Redis.
Human oversight was strictly maintained to enforce guardrails, structure the conversational state graph, and design the HITL (Human-in-the-Loop) intercepts.
