from langchain_core.messages import AIMessage
from app.modules.chat.state import AgentState

class UnrelatedAgent:
    def invoke(self, state: AgentState) -> dict:
        """Immediately returns a canned response for completely unrelated queries without using an LLM."""
        refusal_message = "I am Trendly's customer support assistant. I can only assist you with our products, your orders, store policies, or connecting you to a human agent. I cannot answer unrelated questions."
        return {"messages": [AIMessage(content=refusal_message)]}

unrelated_agent_instance = UnrelatedAgent()
