# test_graph.py

import os
import sys

# Ensure the project root is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from core.graph import web_agent_app
from core.state import AgentState
from langchain_core.messages import HumanMessage

print("--- 1. Testing LangGraph Compilation ---")
try:
    # Attempting to access the compiled graph verifies the imports and structure
    print(f"LangGraph compiled successfully. Graph nodes: {web_agent_app.nodes}")
except Exception as e:
    print(f"LangGraph Compilation FAILED: {e}")
    sys.exit(1)

print("\n--- 2. Testing a Simple Graph Invocation ---")

initial_state: AgentState = {
    "messages": [HumanMessage(content="Initial request: Create a small page.")],
    "user_request": "Create a simple landing page with a green background.",
    "website_code": "",
    "code_updated": False,
    "next_action": ""
}

from app.tools.code_editor import WEBSITE_DIR
import os

try:
    # Running the graph for one cycle
    final_state = web_agent_app.invoke(initial_state)

    print("Invocation Finished.")

    # --- CHECK FINAL OUTPUT ---
    final_html_path = os.path.join(WEBSITE_DIR, "index.html")
    with open(final_html_path, "r") as f:
        final_code = f.read()

    print(f"Final Code Snippet (from saved file): {final_code[:100]}...")
    print(f"Code Updated Status (from final state): {final_state.get('code_updated', False)}")

    # Assertions based on file content and state flow
    assert os.path.exists(final_html_path)
    assert final_code != ""
    print("\nGraph execution logic verified: Code was successfully generated and saved to file.")

except Exception as e:
    print(
        f"LangGraph Invocation FAILED. This could be due to a bug in router/planner/code_agent logic, or LLM issues: {e}")
    sys.exit(1)

print("\n--- LangGraph Workflow Test PASSED ---")