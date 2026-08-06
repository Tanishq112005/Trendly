import os
from langchain_core.messages import SystemMessage
from app.core.llm import llm
from app.modules.chat.state import AgentState


class PolicyAgent:
    def __init__(self):
        self.llm = llm

        data_dir = os.path.join(os.path.dirname(__file__), "../../../../data")
        policy_file = os.path.join(data_dir, "trendly_policy.md")
        self.policy_text = ""
        if os.path.exists(policy_file):
            with open(policy_file, "r", encoding="utf-8") as f:
                self.policy_text = f.read()

    def invoke(self, state: AgentState) -> dict:
        """Answers general questions using the policy. No tools."""
        user_name = state.get("name") or "the customer"
        sys_msg_text = f"You are Trendly's policy assistant. You are speaking to {user_name}. Greet them by their name if you know it. Answer the user's question using ONLY this policy. If the policy document is silent on a topic or does not explicitly cover the user's request, DO NOT invent rules or guess. Instead, explicitly state that you do not know the answer based on the current policy, and offer to connect them to a human agent or create a support ticket. Format your response beautifully using Markdown. Use bolding for emphasis, bullet points for lists, and markdown tables for tabular data (e.g., refund timelines, shipping costs). Make it easy to read and visually appealing.\n\n{self.policy_text}"
        sys_msg = SystemMessage(content=sys_msg_text)
        recent_messages = state["messages"][-10:] if len(state["messages"]) > 10 else state["messages"]
        response = self.llm.invoke([sys_msg] + recent_messages)
        return {"messages": [response]}


policy_agent_instance = PolicyAgent()
