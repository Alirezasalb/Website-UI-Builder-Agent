from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.state import AgentState
from app.core.llm import llm
from app.tools.code_editor import get_current_website_code, save_website_code, code_tools


# 1. Router Agent Node
def router_node(state: AgentState) -> dict:
    """
    Decides the next step based on the user request and current state.
    """

    # 1. Check if the previous node (Code Agent) requested to END
    # This happens when code_agent_node returns {"next_action": "end"}
    if state["next_action"] == "end" and state["code_updated"] == True:
        # If the code was just updated AND the agent thinks the task is finished, we END.
        # Reset next_action to prevent infinite loop on next user prompt
        return {"next_action": "end", "code_updated": False}

    latest_message = state["messages"][-1].content



    # Simple prompt for the LLM to decide the next step
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            "You are a router agent. Your goal is to decide the next step in the web development process. Based on the user's request and the current state (especially if code has been generated), choose the best next action: 'plan' to create a new plan or refine the code, 'execute_tools' to save the generated code, or 'end' if the task is complete and code is saved."),
        HumanMessage(content=f"User request: {state['user_request']}\nLatest action/message: {latest_message}"),
        HumanMessage(content="Decide the next action: 'plan' (to refine code) or 'end' (task complete).")
    ])

    # Correct way to render the prompt to a list of messages:
    rendered_prompt = prompt.format_messages(messages=state["messages"])

    # Pass the list of messages to invoke
    raw_response = llm.invoke(rendered_prompt)

    # Safely extract content (handle both BaseMessage and str return types)
    if hasattr(raw_response, 'content'):
        response_text = raw_response.content
    else:
        response_text = str(raw_response)

    response = response_text.strip().lower()

    if "plan" in response or "refine" in response:
        next_action = "plan"
    else:
        next_action = "end"  # If the LLM doesn't explicitly choose to refine, we end the current loop.

    return {"next_action": next_action, "code_updated": False}


# 2. Planner Agent Node
def planner_node(state: AgentState) -> dict:
    """
    Generates a detailed plan for the Code Agent or updates the existing code
    by first fetching the current code state.
    """
    # Always fetch current code first to provide context
    code_state_message = get_current_website_code.invoke({})

    # Generate the planning prompt
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(f"""You are an expert UI/UX developer and code planner. Your task is to generate a detailed, comprehensive, and complete set of HTML and CSS code to fulfill the user's request. 
        Focus ONLY on UI/UX (HTML, CSS, minimal JavaScript for interactivity).

        {code_state_message}

        If the current code is empty, generate a full, modern, and responsive website UI structure. 
        If code exists, you must make the necessary changes to fulfill the user's request.

        Your response MUST be a single string containing ONLY the **full** HTML body content, **full** CSS for style.css, and **full** JS for script.js, enclosed in code fences. Do NOT include any other text or reasoning.

        Format your output EXACTLY as follows:

        ```html
        ```

        ```css
        /* ... full CSS for style.css here ... */
        ```

        ```javascript
        // ... full JS for script.js here ...
        ```
        """),
        HumanMessage(content=f"User Request: {state['user_request']}")
    ])

    rendered_prompt = prompt_template.format_messages()  # Format the template into messages

    # Pass the list of messages to invoke
    raw_response = llm.invoke(rendered_prompt)


    # Check if we need to extract content from a Message object or use the string directly
    if hasattr(raw_response, 'content'):
        response_content = raw_response.content
    else:
        response_content = str(raw_response)

    # The output to the next node (code_agent) is now a new HumanMessage containing the code plan
    return {"messages": [HumanMessage(content=response_content)], "next_action": "parse_code"}



# 3. Code Agent Node (Parsing and Tool Execution)
def code_agent_node(state: AgentState) -> dict:
    """
    Parses the generated code from the Planner and executes the save_website_code tool.
    """
    planner_output = state["messages"][-1].content

    # Simple regex parsing to extract the code blocks
    import re

    html_match = re.search(r"```html\s*\n(.*?)\n```", planner_output, re.DOTALL)
    css_match = re.search(r"```css\s*\n(.*?)\n```", planner_output, re.DOTALL)
    js_match = re.search(r"```javascript\s*\n(.*?)\n```", planner_output, re.DOTALL)

    html_code = html_match.group(1).strip() if html_match else ""
    css_code = css_match.group(1).strip() if css_match else "/* CSS code not generated */"
    js_code = js_match.group(1).strip() if js_match else "// JS code not generated"

    # Save the code using the tool
    tool_output = save_website_code.invoke({"html_code": html_code, "css_code": css_code, "js_code": js_code})

    # Update the state with the new code and set the update flag
    return {
        "website_code": html_code,  # Storing the body content for simple viewing/review
        "code_updated": True,
        "messages": [HumanMessage(content=tool_output)],
        "next_action": "end"  # Go back to the router to check if the task is finished
    }