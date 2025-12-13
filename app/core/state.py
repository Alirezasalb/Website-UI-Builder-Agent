from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
import operator


# Define the state schema for LangGraph
class AgentState(TypedDict):
    """
    Represents the state of our agentic web development workflow.
    """
    # Conversation history
    messages: Annotated[List[BaseMessage], operator.add]

    # The current user request (e.g., "create a simple blog landing page")
    user_request: str

    # The current HTML/CSS/JS code of the website
    website_code: str

    # A flag to signal if the code was updated and needs to be rendered
    code_updated: bool

    # The agent's decision on the next step
    next_action: str