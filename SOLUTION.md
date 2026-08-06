# Solution Note

## 1. Architecture Overview
The Trendly Agentic Support Assistant is designed using a **Multi-Agent StateGraph Architecture** built on FastAPI, LangGraph, and LangChain. 
Instead of a single massive LLM prompt, the system relies on specialized sub-agents:
- **Router Agent:** Classifies user intent (product, policy, ticket, unrelated).
- **Information Agent:** Extracts and validates authentication details (Email & Phone).
- **Product Agent:** Handles transactional logic (order lookup, returns, cancellations).
- **Policy Agent:** Answers static questions (shipping times, return policies) using RAG.
- **Unrelated Agent:** Rejects out-of-bounds requests and off-topic trivia.

**Data Flow:**
1. **Semantic Cache Check:** FastAPI intercepts incoming requests. If the request semantically matches a previously answered policy question, the Pinecone Vector DB returns the cached answer immediately in <100ms (saving LLM cost and time).
2. **LangGraph Processing:** If no cache hit, the query enters the StateGraph, gets routed to the appropriate agent, and tools are executed.
3. **HITL Intercept:** If a tool triggers a human escalation, the state is paused, and the LLM response is returned for user confirmation.
4. **Cache Storage:** If the query was a policy question, the LLM's response is asynchronously saved back into the Pinecone Vector Store.

## 2. Key Trade-offs
- **Groq LLM (Free Tier) vs. OpenAI:** We opted for Groq (Llama-3) to keep costs at zero. However, Groq's strict rate limits (429 errors) and fragile function-calling parsing necessitated custom anti-loop prompts and `try/except` fallbacks that wouldn't be strictly necessary with GPT-4.
- **In-Memory Checkpointing vs. Persistent DB:** LangGraph state is currently managed using `MemorySaver()`. While this is extremely fast for local testing, it prevents horizontal scaling. A production environment would require swapping this for a Persistent Checkpointer (like PostgreSQL or MongoDB).
- **FastAPI BackgroundTasks vs. Dedicated Queue:** We opted to handle asynchronous embedding generation for the semantic cache using FastAPI's lightweight `BackgroundTasks` rather than a robust worker queue (like Celery + Redis). This keeps the project easily deployable on a single free-tier Render server.

## 3. Known Limitations
- **Rate Limits:** Rapid consecutive messages will trigger Groq's rate limits, causing the server to pause and wait for the limit window to reset.
- **Stateless Routing for Caching:** The semantic cache currently checks the raw query *before* routing. While effective, a production setup should route first, and *only* check the cache if the intent is classified as a policy query, preventing order-specific queries from accidentally colliding with cached policy answers.

## 4. Five Discovery Questions for Trendly's Ops Team
Before building this for real, we would need to ask:
1. **Authentication:** Do customers typically chat while logged into their accounts (providing a JWT token), or do we need to dynamically ask for PII (email/phone) in the chat window?
2. **Action Automation vs. Ticketing:** For actions like "process a return," do you want the Agent to actually trigger a refund via the payment gateway API, or just create a Zendesk/Freshdesk ticket for an agent to click "Approve"?
3. **Handoff Protocol:** When a ticket is escalated, what CRM system are we pushing to? Do you need WebSockets to seamlessly bridge a live human agent into the chat, or is an async email ticket sufficient?
4. **Edge Case Priority:** For cases like "Delayed > 3 days," does the ₹250 store credit need to be generated as a dynamic coupon code via Shopify/Magento API, or just promised in text?
5. **Analytics:** What metrics are most important for you to track? (e.g., Containment Rate, Average Handle Time, Fallback Rate).
