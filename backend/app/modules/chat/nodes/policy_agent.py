import os
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.core.config import GROQ_API_KEY
from app.modules.chat.state import AgentState

class PolicyAgent:
    def __init__(self):
        self.llm = ChatGroq(api_key=GROQ_API_KEY, model="llama-3.1-8b-instant", temperature=0)
        
        data_dir = os.path.join(os.path.dirname(__file__), "../../../../../data")
        policy_file = os.path.join(data_dir, "trendly_policy.md")
        self.policy_text = ""
        if os.path.exists(policy_file):
            with open(policy_file, "r", encoding="utf-8") as f:
                self.policy_text = f.read()

    def invoke(self, state: AgentState) -> dict:
        """Answers general questions using the policy. No tools."""
        sys_msg = SystemMessage(content=f"You are Trendly's policy assistant. Answer the user's question using ONLY this policy. Do NOT invent rules.\n\n{self.policy_text}")
        response = self.llm.invoke([sys_msg] + state["messages"])
        return {"messages": [response]}

policy_agent_instance = PolicyAgent()
