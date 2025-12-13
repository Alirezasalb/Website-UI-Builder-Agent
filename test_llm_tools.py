# test_llm_tools.py

import os
import sys
import shutil

# Ensure the project root is in path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from core.llm import llm  # Should load the model or the MockLLM
from tools.code_editor import save_website_code, get_current_website_code, WEBSITE_DIR

print("--- 1. Testing LLM Loading ---")
print(f"LLM class: {type(llm).__name__}")

# If using a mock, the response will be predictable
test_prompt = "Tell me the capital of France."
try:
    llm_response = llm.invoke(test_prompt)
    print(f"LLM Test Successful. Response start: {llm_response[:50]}...")
except Exception as e:
    print(f"LLM Test FAILED: {e}")
    sys.exit(1)

print("\n--- 2. Testing Code Tools ---")
# Clean up previous runs
if os.path.exists(WEBSITE_DIR):
    shutil.rmtree(WEBSITE_DIR)
os.makedirs(WEBSITE_DIR)

TEST_HTML = "<h1>Hello, World!</h1>"
TEST_CSS = "body { background-color: lightblue; }"

# Test save tool
try:
    # Use .invoke() with a dictionary of inputs, as required by LangChain StructuredTool
    save_result = save_website_code.invoke({"html_code": TEST_HTML, "css_code": TEST_CSS})
    print(f"Save Tool Result: {save_result}")

    # Verify files exist
    assert os.path.exists(os.path.join(WEBSITE_DIR, "index.html"))
    assert os.path.exists(os.path.join(WEBSITE_DIR, "style.css"))
    print("Files creation verified.")
except Exception as e:
    print(f"Save Tool FAILED: {e}")
    sys.exit(1)

# Test read tool
try:
    # Use .invoke() with an empty dictionary for tools that take no arguments
    read_result = get_current_website_code.invoke({})
    print("\nRead Tool Result (should contain HTML/CSS):")
    print(read_result)

    # Basic check to see if content was read
    assert "<h1>Hello, World!</h1>" in read_result
    print("Read Tool verification successful.")
except Exception as e:
    print(f"Read Tool FAILED: {e}")
    sys.exit(1)

print("\n--- LLM and Tool Configuration Test PASSED ---")