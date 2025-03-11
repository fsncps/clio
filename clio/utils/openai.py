import os
from clio.utils.markdown_utils import render_markdown  # ✅ Use the existing markdown function
from clio.core.state import app_state
from clio.utils.logging import log_message
from openai import OpenAI
import time


# OpenAI API key (Set this in your environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")



def generate_title_ai():
    """Send markdown to OpenAI assistant and retrieve a concise title (max 4 words)."""

    if not app_state.current_UUID:
        log_message("No record selected for AI title generation.", "warning")
        return None

    markdown_text = render_markdown(app_state.current_content)  # ✅ Convert content to markdown

    client = OpenAI()

    # ✅ Step 1: Create a thread and run it
    run = client.beta.threads.create_and_run(
        assistant_id="asst_DXFpBka8vb7unu6jifZOLh6q",
        thread={
            "messages": [
                {"role": "user", "content": f"Here is your markdown text: Analyze and return the most adequate title, no more than four words: {markdown_text}"}
            ]
        }
    )

    thread_id = run.thread_id  # ✅ Extract thread ID
    run_id = run.id  # ✅ Extract run ID

    log_message(f"Started AI title generation: {thread_id}, Run ID: {run_id}", "info")

    # ✅ Step 2: Wait for the assistant to finish processing
    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run_status.status in ["completed", "failed", "cancelled"]:
            break  # ✅ Stop polling once complete
        time.sleep(1)  # ✅ Wait a moment before checking again

    if run_status.status != "completed":
        log_message(f"OpenAI Assistant failed to generate a title: {run_status.status}", "error")
        return None

    # ✅ Step 3: Retrieve the messages from the thread
    thread_messages = client.beta.threads.messages.list(thread_id=thread_id)

    # ✅ Step 4: Extract the assistant's response
    title = None
    for message in thread_messages.data:
        if message.role == "assistant":
            title = message.content[0].text.value.strip()  # ✅ Extract text response
            break  # ✅ Only take the first assistant response

    if not title:
        log_message("No response received from OpenAI Assistant.", "error")
        return None

    log_message(f"Generated AI Title: {title}", "info")
    return title

