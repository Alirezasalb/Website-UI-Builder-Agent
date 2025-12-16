# app/api/routes.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage
from app.core.graph import web_agent_app
from app.core.state import AgentState
from app.tools.code_editor import WEBSITE_DIR
import os

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")

# Simple state manager (in-memory, replace with persistent storage for production)
user_session_state: AgentState = {
    "messages": [],
    "user_request": "",
    "website_code": "",
    "code_updated": False,
    "next_action": ""
}


@router.get("/", response_class=HTMLResponse)
async def home_view(request: Request):
    """Serve the main agent UI."""
    try:
        with open(os.path.join(WEBSITE_DIR, "index.html"), "r") as f:
            full_html = f.read()
    except FileNotFoundError:
        full_html = ""

    # Preprocess messages for safe Jinja2 rendering
    chat_history = []
    for msg in user_session_state["messages"]:
        msg_type = "user" if isinstance(msg, HumanMessage) else "agent"
        chat_history.append({
            "type": msg_type,
            "content": str(msg.content).strip()
        })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "chat_history": chat_history,
            "website_code": full_html,
        }
    )


@router.post("/process_request")
async def process_request(request: Request, user_prompt: str = Form(...)):
    """Handles the user prompt and runs the LangGraph agent."""
    global user_session_state

    # Reset code_updated flag
    user_session_state["code_updated"] = False

    # Initialize the state for the new invocation
    user_session_state["user_request"] = user_prompt
    user_session_state["messages"].append(HumanMessage(content=user_prompt))

    # Run the LangGraph workflow
    # We run it once. The agent's loop handles multi-step work until it hits END.
    try:
        # Note: LangGraph's invoke returns the final state after the graph completes
        final_state = await web_agent_app.ainvoke(user_session_state)

        # Update the session state
        user_session_state = final_state

        # Add a final confirmation message
        if final_state.get("website_code"):
            user_session_state["messages"].append(
                HumanMessage(content="Workflow complete. Website code has been updated."))

    except Exception as e:
        print(f"AGENT ERROR: {e}")
        user_session_state["messages"].append(HumanMessage(content=f"An error occurred during workflow: {e}"))

    # Redirect back to the home page to show the result and updated code
    return RedirectResponse(url="/", status_code=303)


@router.get("/sandbox/{path:path}", response_class=HTMLResponse)
async def sandbox_view(path: str = "index.html"):
    """Serves files from the website_sandbox directory (the website itself)."""
    file_path = os.path.join(WEBSITE_DIR, path)

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()

        # Simple content-type detection
        if file_path.endswith(".css"):
            return HTMLResponse(content, media_type="text/css")
        elif file_path.endswith(".js"):
            return HTMLResponse(content, media_type="application/javascript")
        else:
            return HTMLResponse(content, media_type="text/html")

    return HTMLResponse("<h1>404 Not Found in Sandbox</h1>", status_code=404)