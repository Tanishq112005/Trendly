import re
from langchain_core.messages import AIMessage
from app.modules.chat.state import AgentState

class GuardrailAgent:
    def invoke(self, state: AgentState) -> dict:
        """
        Intercepts the final AI message before it reaches the user and forcefully 
        replaces it if it violates Section 7 of the Trendly Policy.
        """
        last_msg = state["messages"][-1]
        
        # Only scan AI messages (not user input or tool outputs)
        if not isinstance(last_msg, AIMessage):
            return {}
            
        content = last_msg.content.lower()
        
        # Section 7: Do not collect bank account numbers, card numbers, or CVV in chat
        if re.search(r'\b(cvv|bank account|routing number|credit card|debit card)\b', content):
            return {"messages": [AIMessage(content="POLICY BLOCK: I am not authorized to collect or discuss bank account numbers, card numbers, or CVVs in chat. Please wait for a human agent to contact you securely.")]}
            
        # Section 7: Do not offer discounts, coupons, waivers, or goodwill credits
        if re.search(r'\b(coupon|discount|waiver|goodwill)\b', content):
            return {"messages": [AIMessage(content="POLICY BLOCK: I am not authorized to offer discounts, coupons, waivers, or goodwill credits not defined in the policy.")]}
            
        # Section 7: Do not give medical, legal, or financial advice
        if re.search(r'\b(medical advice|legal advice|financial advice|prescription)\b', content):
            return {"messages": [AIMessage(content="POLICY BLOCK: I cannot provide medical, legal, or financial advice.")]}

        # If it passes all checks, return nothing (which tells LangGraph to keep the original message)
        return {}

guardrail_agent = GuardrailAgent()
