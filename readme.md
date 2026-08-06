# Trendly Agentic Support Assistant

## 📌 Project Overview
An autonomous AI agent built for Trendly to handle customer support inquiries, track orders, process policy queries, and intelligently escalate tickets to humans. 

This project is an advanced multi-agent backend architecture designed to handle customer support interactions efficiently. It operates on a Client-Server model via REST API and leverages Large Language Models (LLMs) using **LangChain** and **LangGraph** to dynamically process, route, and resolve user queries. The system also features a robust ticketing mechanism with Human-In-The-Loop (HITL) confirmation.

---


## 📸 System Previews

![Image 1](photos/image1.png)
![Image 2](photos/image2.png)
![Image 3](photos/image3.png)
![Image 4](photos/image4.png)
![Image 5](photos/image5.png)
![Image 6](photos/image6.png)
![Image 7](photos/image7.png)
![Image 8](photos/image8.png)
![Image 9](photos/image9.png)
![Image 10](photos/image10.png)


## 🏗️ Architecture & Technologies

- **Frameworks:** FastAPI, LangChain, LangGraph (Multi-Agent System)
- **LLM:** Groq (Llama-3)
- **Databases:** 
  - **Vector Store (PINECONE):** Stores FAQs for Semantic Caching. Uses semantic search to instantly answer recurring user problems.
  - **MongoDB:** Asynchronously stores generated support tickets and AI summaries for Ticket Management.
  - **Redis (For Background services)** : For running the worker , which asynchronously , saves the tickets and summary in the database , we use redis 
- **Data Source:** User profiles and `order.json` (for order history and SKU details).
- **Communication:** REST API.

### Client-Server Architecture
The system operates on a standard Request-Response cycle using REST APIs. 

```mermaid
graph TD
    classDef client fill:#1d4ed8,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef server fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef note fill:#dc2626,stroke:#991b1b,stroke-width:2px,color:#fff;

    C([Client]):::client <-->|REST API Request / Response| S[Server]:::server
    
    S -.- N>⚠️ Error 429: Too Many Requests<br/>Triggered due to free API tier rate limits]:::note
```

---

## 🚀 Setup Instructions

### 1. Requirements
Ensure you have Python 3.10+ installed.

### 2. Environment Variables
Create a `.env` file in the **backend** directory:
```env
GROQ_API_KEY=your_groq_key
MONGODB_URI=your_mongo_uri
REDIS_URI=your_redis_uri
HUGGING_FACE=your_hf_token
VECTOR_DB=your_vector_db_uri
NOMIC_API=your_nomic_api_key
```

Create a `.env` file in the **frontend** directory:
```env
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

### 3. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 4. Run the Servers
Use `honcho` to start the backend server and its related processes:
```bash
honcho start
```
Your chat endpoint will be available at `POST http://127.0.0.1:8000/api/chat/` (or as configured in your Procfile).

### 5. Running Tests
You can run the end-to-end test suite included in the repository:
```bash
python test_e2e.py
```

---

## 👥 User Roles & Permissions

1. **User / Client**
   - Interacts with the multi-agent chatbot.
   - Can raise support tickets (requires explicit Yes/No confirmation).
2. **Admin**
   - **Credentials:** `username: admin` | `password: password`
   - Has exclusive access to view and resolve user tickets stored in MongoDB.
   - Views AI-generated ticket summaries.
   - *Future Scope:* Implement an email service for admins to directly answer users.

---

## 🤖 Multi-Agent Workflow

The core of the application relies on an intelligent routing mechanism that analyzes the user query and directs it to the appropriate specialized agent. 

### 1. The Core Routing Flow (ReAct System)
The multi-agent system operates in a **Reasoning and Acting (ReAct) loop**. Once a query is processed and answered by a specific agent, the workflow concludes the cycle and loops back, ready to accept and route the next user query.

```mermaid
graph TD
    classDef startEnd fill:#1d4ed8,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef agent fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef router fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef guard fill:#dc2626,stroke:#991b1b,stroke-width:2px,color:#fff;

    Q([User Query]):::startEnd --> GR[Guard Rail Agent]:::guard
    GR -- "Checks Section 7 Friendly Policy" --> R((Router Agent)):::router
    
    %% Routing to Agents
    R -- "Routes based on context" --> PA[Product Agent]:::agent
    R --> PoA[Policy Agent]:::agent
    R --> TA[Ticket Agent]:::agent
    R --> UA[Unrelated Agent]:::agent
    
    %% Resolving and ReAct Loop
    PA --> End([End of Turn / Response Sent]):::startEnd
    PoA --> End
    TA --> End
    UA --> End
    
    End -. "ReAct Loop: Waits for next query" .-> Q
```

---

### 2. Product Agent Logic
The Product Agent handles order-specific inquiries. It intelligently extracts order details and scopes the prompt to specific orders when available.

```mermaid
graph TD
    classDef startEnd fill:#1d4ed8,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef action fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef decision fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff;

    Start([Query Classified as Product]):::startEnd --> C{Check Email & Phone in State}:::decision
    
    %% Email/Phone Not Present Branch
    C -- "Not Present" --> AskEP[Ask for Email & Phone]:::action
    AskEP --> AbstractEP[Abstract Email & Phone]:::action
    
    %% Parallel branches for saving email and phone
    AbstractEP --> SaveEmail[Save Email]:::action
    AbstractEP --> SavePhone[Save Phone]:::action
    
    SaveEmail --> CheckGiven{If Both Present}:::decision
    SavePhone --> CheckGiven
    
    CheckGiven -- "Yes" --> ExtractList[Extract whole orders list from order.json]:::action
    CheckGiven -- "If not give" --> ExtractSKU[Extract SKU name & Save to State]:::action
    
    %% Email/Phone Present Branch
    C -- "Present" --> CheckOrder{Order ID in Query?}:::decision
    CheckOrder -- "No" --> AskOrder[Ask User for Order ID]:::action
    AskOrder --> ExtractOrder
    CheckOrder -- "Yes" --> ExtractOrder[Extract Order ID & Save to State Space]:::action
    
    %% Prompting logic
    ExtractOrder --> SendPrompt[Send ONLY the particular order in prompt]:::action
    ExtractList --> AgentAnswer
    ExtractSKU --> AgentAnswer
    SendPrompt --> AgentAnswer[Agent answers user query based on Policy & State Space]:::action
    
    AgentAnswer --> Finish([End]):::startEnd
```

---

### 3. Ticket Agent & Human-in-the-Loop (HITL)
If a user needs to raise a ticket, the system ensures they actually want to proceed by pausing execution and waiting for user confirmation.

```mermaid
graph TD
    classDef startEnd fill:#1d4ed8,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef action fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef decision fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef pause fill:#ea580c,stroke:#c2410c,stroke-width:2px,color:#fff,stroke-dasharray: 5 5;
    classDef db fill:#2563eb,stroke:#1d4ed8,stroke-width:2px,color:#fff;

    Start([Router Agent -> Ticket Agent]):::startEnd --> CheckID{Order ID Present?}:::decision
    
    CheckID -- "No" --> AskID[Ask for Order ID]:::action
    AskID --> CheckID
    
    CheckID -- "Yes" --> PrepTicket[Prepare the Ticket]:::action
    PrepTicket --> Pause((System Pause)):::pause
    
    Pause -. "Human-In-The-Loop" .-> Conf{User Confirms Yes/No}:::decision
    
    Conf -- "Yes" --> Greet[Greet: 'Your ticket is created']:::action
    Greet --> Finish([End]):::startEnd
    
    Conf -- "Async Process" --> AsyncGen[LLM Generates Summary]:::action
    AsyncGen --> AsyncSave[(MongoDB)]:::db
```

---

### 4. Policy Agent Logic
Handles queries related to general policies and FAQs. Checks the VectorDB first; if not found, routes to a policy-aware LLM.

```mermaid
graph TD
    classDef startEnd fill:#1d4ed8,stroke:#1e3a8a,stroke-width:2px,color:#fff;
    classDef action fill:#059669,stroke:#047857,stroke-width:2px,color:#fff;
    classDef decision fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef db fill:#2563eb,stroke:#1d4ed8,stroke-width:2px,color:#fff;

    Start([Router Agent -> Policy Agent]):::startEnd --> CheckFAQ{Search VectorDB}:::decision
    
    CheckFAQ -- "Found" --> ReturnDirect[Return Answer Instantly]:::action
    CheckFAQ -- "If Not Present" --> LLM[Route to LLM with complete Friendly-Policy]:::action
    
    LLM --> AnsUser[Answer User Query]:::action
    AnsUser --> AsyncSave[(Save in DB Asynchronously)]:::db
    
    ReturnDirect --> Finish([End]):::startEnd
    AsyncSave --> Finish
```

---

## 🤖 AI-Usage Note
This project was built with the assistance of advanced LLMs (Claude/GPT) for:
- Writing boilerplate FastAPI routes and Pydantic schemas.
- Refactoring the LangGraph multi-agent architecture (splitting monolithic agents into smaller specialized nodes).
- Debugging edge cases like Pydantic AttributeErrors and Groq tool-calling JSON parsing failures.
- Designing the Semantic Caching layer with LangChain Redis.

## Render Problem 
- It Might we chance that the you did not get the message too fast in the first attempt , because the i deploy on the render server , and it takes 50 sec time to wakes up

*Human oversight was strictly maintained to enforce guardrails, structure the conversational state graph, and design the HITL (Human-in-the-Loop) intercepts.*
