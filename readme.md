# Trendly Agentic Support Assistant

This is the backend for the Trendly customer support AI, built with FastAPI, LangGraph, and Groq (LLaMA-3).

## Prerequisites
1. Python 3.10+
2. A valid Groq API Key

## Setup & Running

1. **Navigate to the backend folder**:
   ```bash
   cd backend
   ```

2. **Activate the virtual environment**:
   ```bash
   venv\Scripts\activate
   ```

3. **Set your Environment Variables**:
   Open the `backend/.env` file and paste your Groq API Key:
   ```env
   GROQ_API_KEY=gsk_your_key_here
   ```

4. **Start the Server**:
   ```bash
   python run.py
   ```

## Testing
Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser to access the interactive Swagger UI and test the `/api/chat/` endpoint.