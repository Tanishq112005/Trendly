from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from app.core.config import GROQ_API_KEY
from app.modules.chat.state import AgentState


class RouterDecision(BaseModel):
    intent: str = Field(
        description="The user's intent. Must be exactly 'product', 'ticket', 'policy', or 'unrelated'."
    )


class RouterAgent:
    def __init__(self):
        self.llm = ChatGroq(
            api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0
        )
        self.structured_llm = self.llm.with_structured_output(RouterDecision)

    def invoke(self, state: AgentState) -> dict:
        """The logical agent that divides the user query using structured output."""
        recent_messages = state["messages"][-4:]
        history_text = "\n".join(
            [
                f"{'AI' if msg.type == 'ai' else 'User'}: {msg.content}"
                for msg in recent_messages
            ]
        )

        prompt = f"""You are a strict routing agent for Trendly. Read the conversation history and classify the USER's latest intent into exactly ONE of these categories:
        1. 'product': If they are asking about order status, tracking, returns, OR providing requested details like email, phone number, or order ID.
        2. 'ticket': If they are explicitly asking for a human, a manager, or to create a support ticket.
        3. 'policy': If they are asking general questions about shipping, returns, or shop rules.
        4. 'unrelated': If the user is asking general trivia, coding questions, or anything completely unrelated to Trendly.
        
        Recent Conversation History:
        {history_text}
        
        Based on the User's latest message in the history, what is their intent?
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
