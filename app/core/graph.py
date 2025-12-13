from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.core.agents import router_node, planner_node, code_agent_node


# Define the graph
def build_agent_graph():
    workflow = StateGraph(AgentState)

    # Add the nodes
    workflow.add_node("router", router_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("code_agent", code_agent_node)

    # Set the entry point
    workflow.set_entry_point("router")

    # Define the edges (flow)

    # Router conditional logic
    def route_decision(state: AgentState) -> str:
        """Determines the next step based on the Router Agent's decision."""
        if state["next_action"] == "plan":
            return "planner"
        elif state["next_action"] == "execute_tools":
            return "code_agent"
        else:  # "end"
            return END

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "planner": "planner",
            "code_agent": "code_agent",
            END: END
        }
    )

    # Planner always passes to the Code Agent to parse and save
    workflow.add_edge("planner", "code_agent")

    # Code Agent goes back to the Router for a final check or to finish
    workflow.add_edge("code_agent", "router")

    # Compile the graph
    app = workflow.compile()

    return app


# The compiled LangGraph application instance
web_agent_app = build_agent_graph()