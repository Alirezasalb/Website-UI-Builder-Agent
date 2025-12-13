import os
from langchain.tools import tool
from app.core.llm import llm

# Assuming WEBSITE_DIR is defined here or imported
WEBSITE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "website_sandbox")

if not os.path.exists(WEBSITE_DIR):
    os.makedirs(WEBSITE_DIR)




def initialize_website_sandbox():
    """Ensures the sandbox directory and basic files exist."""
    os.makedirs(WEBSITE_DIR, exist_ok=True)

    # Create empty placeholder files if they don't exist
    for filename in ["index.html", "style.css", "script.js"]:
        filepath = os.path.join(WEBSITE_DIR, filename)
        if not os.path.exists(filepath):
            with open(filepath, "w") as f:
                # Provide a basic HTML structure to prevent a blank page error on first load
                if filename == "index.html":
                    f.write(
                        "<!DOCTYPE html>\n<html><head><title>Loading...</title><link rel='stylesheet' href='style.css'></head><body><h1>Agent Initializing...</h1></body></html>")
                else:
                    f.write("")  # Empty content for CSS/JS



@tool
def save_website_code(html_code: str, css_code: str = "", js_code: str = "") -> str:
    """
    Saves the provided HTML, CSS, and JavaScript code to a file system.
    The HTML is saved to index.html, CSS to style.css, and JS to script.js
    in the website_sandbox directory. Returns the confirmation message.
    """
    index_html_path = os.path.join(WEBSITE_DIR, "index.html")
    style_css_path = os.path.join(WEBSITE_DIR, "style.css")
    script_js_path = os.path.join(WEBSITE_DIR, "script.js")

    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Generated Website</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
{html_code}
    <script src="script.js"></script>
</body>
</html>
    """

    with open(index_html_path, "w") as f:
        f.write(full_html)

    with open(style_css_path, "w") as f:
        f.write(css_code)

    with open(script_js_path, "w") as f:
        f.write(js_code)

    return "Code saved successfully. The website is now updated in the sandbox."


@tool
def get_current_website_code() -> str:
    """
    Reads and returns the current state of the website code (index.html, style.css, script.js)
    from the website_sandbox directory for the AI to review.
    """
    index_html_path = os.path.join(WEBSITE_DIR, "index.html")
    style_css_path = os.path.join(WEBSITE_DIR, "style.css")
    script_js_path = os.path.join(WEBSITE_DIR, "script.js")

    html_code = ""
    css_code = ""
    js_code = ""

    try:
        with open(index_html_path, "r") as f:
            # Only read the content inside the <body> tag for the agent
            content = f.read()
            body_start = content.find("<body>") + len("<body>")
            body_end = content.find("</body>")
            html_code = content[body_start:body_end].strip()

        with open(style_css_path, "r") as f:
            css_code = f.read()

        with open(script_js_path, "r") as f:
            js_code = f.read()

        return (
            "**CURRENT WEBSITE CODE**:\n"
            f"HTML (body content):\n```html\n{html_code}\n```\n"
            f"CSS (style.css):\n```css\n{css_code}\n```\n"
            f"JS (script.js):\n```javascript\n{js_code}\n```"
        )
    except FileNotFoundError:
        return "No website code found. Start by generating the initial structure."


# Combine tools
code_tools = [save_website_code, get_current_website_code]