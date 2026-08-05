from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.llm import llm
from app.modules.chat.state import AgentState


class RouterDecision(BaseModel):
    intent: str = Field(
        description="The user's intent. Must be exactly 'product_agent', 'ticket_agent', 'policy_agent', or 'unrelated_agent'."
    )

class RouterAgent:
    def __init__(self):
        self.llm = llm
        self.structured_llm = self.llm.with_structured_output(RouterDecision)
        
    def invoke(self, state: AgentState) -> dict:
        """The logical agent that divides the user query using structured output."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a strict routing agent for Trendly. 
        Read the conversation history and classify the USER's latest intent into exactly ONE of these agents:
        
        1. 'product_agent': If they are asking about order status, tracking, returns, account details, OR providing their email/phone number.
        2. 'ticket_agent': If they are explicitly asking for a human, a manager, or to create a support ticket.
        3. 'policy_agent': If they are asking general questions about shipping, returns, or shop rules.
        4. 'unrelated_agent': If the user is asking general trivia, coding questions, or anything completely unrelated to Trendly.
        """),
            ("placeholder", "{messages}")
        ])

        # Use the LCEL chain to invoke the structured LLM
        decision = prompt | self.structured_llm
        result = decision.invoke({"messages": state["messages"]})
        
        return {"next_node": result.intent}


router_agent = RouterAgent()
