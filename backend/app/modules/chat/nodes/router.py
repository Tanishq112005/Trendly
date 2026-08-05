from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from app.core.config import GROQ_API_KEY
from app.modules.chat.state import AgentState

class RouterDecision(BaseModel):
    intent: str = Field(description="The user's intent. Must be exactly 'product', 'ticket', 'policy', or 'unrelated'.")

class RouterAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0)
        self.structured_llm = self.llm.with_structured_output(RouterDecision)

    def invoke(self, state: AgentState) -> dict:
        """The logical agent that divides the user query using structured output."""
        last_message = state["messages"][-1].content
        
        prompt = f"""You are a strict routing agent for Trendly. Read the user's message and classify it into exactly ONE of these categories:
        1. 'product': If they are asking about order status, tracking, return/exchange eligibility, OR if they are providing their email, phone number, or order ID.
        2. 'ticket': If they are explicitly asking for a human, a manager, or to create a support ticket.
        3. 'policy': If they are asking general questions about shipping, returns, or shop rules.
        4. 'unrelated': If the user is asking general trivia (like the capital of a country), coding questions, or anything completely unrelated to shopping at Trendly.
        
        User Message: "{last_message}"
        """
        
        response = self.structured_llm.invoke([SystemMessage(content=prompt)])
        decision = response.intent.strip().lower()
        
        if "product" in decision:
            return {"next_node": "product_agent"}
        elif "ticket" in decision:
            return {"next_node": "ticket_agent"}
        elif "unrelated" in decision:
            return {"next_node": "unrelated_agent"}
        else:
            return {"next_node": "policy_agent"}

router_agent = RouterAgent()
