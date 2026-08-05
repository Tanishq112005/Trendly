import re
from langchain_core.messages import AIMessage
from app.modules.chat.state import AgentState
from langchain_core.messages import HumanMessage





## Gaurdrail Agent , Intercepts the user's message before routing and forcefully blocks it if it violates Section 7 of the Trendly Policy.
class GuardrailAgent:
    def invoke(self, state: AgentState) -> dict:
       
        last_msg = state["messages"][-1]

        # Scan the user's incoming message
        if not isinstance(last_msg, HumanMessage):
            return {}

        content = last_msg.content.lower()

        # Section 7: Do not collect bank account numbers, card numbers, or CVV in chat
        if re.search(
            r"\b(cvv|bank account|routing number|credit card|debit card)\b", content
        ):
            return {
                "messages": [
                    AIMessage(
                        content="POLICY BLOCK: I am not authorized to collect or discuss bank account numbers, card numbers, or CVVs in chat. Please wait for a human agent to contact you securely."
                    )
                ],
                "next_node": "END"
            }

        # Section 7: Do not offer discounts, coupons, waivers, or goodwill credits
        if re.search(r"\b(coupon|discount|waiver|goodwill)\b", content):
            return {
                "messages": [
                    AIMessage(
                        content="POLICY BLOCK: I cannot discuss or offer unauthorized discounts, coupons, waivers, or goodwill credits."
                    )
                ],
                "next_node": "END"
            }

        # Section 7: Do not give medical, legal, or financial advice
        if re.search(
            r"\b(medical advice|legal advice|financial advice|prescription)\b", content
        ):
            return {
                "messages": [
                    AIMessage(
                        content="POLICY BLOCK: I cannot provide medical, legal, or financial advice."
                    )
                ],
                "next_node": "END"
            }

        # If safe, route to the router!
        return {"next_node": "router_node"}

guardrail_agent = GuardrailAgent()
