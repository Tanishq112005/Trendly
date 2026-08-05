from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from app.modules.chat.state import AgentState

from app.modules.chat.nodes.router import router_agent
from app.modules.chat.nodes.policy_agent import policy_agent_instance
from app.modules.chat.nodes.product_agent import product_agent_instance
from app.modules.chat.nodes.ticket_agent import ticket_agent_instance
from app.modules.chat.nodes.unrelated_agent import unrelated_agent_instance
from app.modules.chat.tools import OrderTools, TicketTools

class GraphManager:
    def __init__(self):
        self.builder = StateGraph(AgentState)
        self.memory = MemorySaver()
        self.graph = None
        self._build_graph()

    @staticmethod
    def route_after_router(state: AgentState) -> str:
        return state["next_node"]

    @staticmethod
    def check_exit(state: AgentState) -> str:
        if not state["messages"]:
            return "router_node"
        last_msg = state["messages"][-1].content.lower().strip()
        if last_msg in ["quit", "exit", "stop"]:
            return END
        return "router_node"

    def _build_graph(self):
        # Nodes
        self.builder.add_node("router_node", router_agent.invoke)
        self.builder.add_node("policy_agent", policy_agent_instance.invoke)
        self.builder.add_node("product_agent", product_agent_instance.invoke)
        self.builder.add_node("ticket_agent", ticket_agent_instance.invoke)
        self.builder.add_node("unrelated_agent", unrelated_agent_instance.invoke)

        all_tools = [OrderTools.lookup_order, OrderTools.check_return_eligibility, TicketTools.escalate_to_human]
        self.builder.add_node("tools", ToolNode(all_tools))
        
        # Add Guardrail Node
        from app.modules.chat.nodes.guardrail import guardrail_agent
        self.builder.add_node("guardrail", guardrail_agent.invoke)

        # Edges
        self.builder.add_conditional_edges(START, self.check_exit, {"router_node": "router_node", END: END})
        self.builder.add_conditional_edges("router_node", self.route_after_router, {
            "product_agent": "product_agent",
            "policy_agent": "policy_agent",
            "ticket_agent": "ticket_agent",
            "unrelated_agent": "unrelated_agent"
        })

        # Route to Guardrail instead of END
        self.builder.add_edge("policy_agent", "guardrail")
        self.builder.add_conditional_edges("product_agent", tools_condition, {"tools": "tools", END: "guardrail"})
        self.builder.add_conditional_edges("ticket_agent", tools_condition, {"tools": "tools", END: "guardrail"})

        self.builder.add_conditional_edges("tools", self.route_after_router, {
            "product_agent": "product_agent",
            "ticket_agent": "ticket_agent"
        })
        
        # Guardrail is the final step before returning to the user
        self.builder.add_edge("guardrail", END)

        self.graph = self.builder.compile(checkpointer=self.memory)

graph_manager = GraphManager()
graph = graph_manager.graph
