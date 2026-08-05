from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import GROQ_API_KEY
from app.modules.chat.state import AgentState
from app.modules.chat.tools import TicketTools

class TicketAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0)
        self.tools = [TicketTools.escalate_to_human]
        self.ticket_llm = self.llm.bind_tools(self.tools)

    def invoke(self, state: AgentState) -> dict:
        """Handles escalation to human."""
        sys_msg = SystemMessage(content="""You handle human escalations for Trendly. 
1. Ask the user for confirmation before escalating. Use the escalate tool.
2. STRICT RULES: Do NOT offer unauthorized discounts. Do NOT ask for or collect bank details or card numbers. If a refund requires bank details, state that a human agent will collect them securely via email.
""")
        response = self.ticket_llm.invoke([sys_msg] + state["messages"])
        return {"messages": [response]}

ticket_agent_instance = TicketAgent()
