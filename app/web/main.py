from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import uvicorn
import os
# Import the function only; we will call it inside the startup event
from app.tools.code_editor import initialize_website_sandbox

# --- Initialize the FastAPI application instance ---
app = FastAPI(title="Agentic Website Builder")


# --- Use FastAPI's Startup Event for Initialization (THE FIX) ---
@app.on_event("startup")
async def startup_event():
    """
    Runs initialization logic after all modules and dependencies are loaded.
    This prevents NameErrors and ImportErrors caused by circular module loading.
    """
    print("Initializing Website Sandbox...")
    initialize_website_sandbox()

    # We remove the redundant os.makedirs call here, as it's handled by initialize_website_sandbox()

    # CRITICAL: Mount the static files for the main application's CSS/JS
    # The 'static' directory contains the CSS that styles the whole chat interface.
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")


# 1. Mount the StaticFiles handler for the *website content*
# This serves the files created by the agent for the iframe.
app.mount(
    "/sandbox_static",
    StaticFiles(directory="app/website_sandbox"),
    name="website_sandbox_static"
)

# Include the API routes
app.include_router(router)

# --- Optional Main Execution Block ---
if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=7051)