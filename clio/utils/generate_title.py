import sys
import time
from openai import OpenAI

# --- Minimal content mock for markdown rendering ---
class MinimalContent:
    def __init__(self, text: str):
        self.text = text
        self.header = ""

# --- Minimal inline markdown renderer ---
def render_markdown(content) -> str:
    lines = []
    if hasattr(content, "header") and content.header:
        lines.append(f"# {content.header}")
    if hasattr(content, "text") and content.text:
        lines.append(content.text)
    return "\n\n".join(lines)

# --- Title generation ---
def generate_title_from_text(text: str) -> str | None:
    try:
        content = MinimalContent(text)
        markdown = render_markdown(content)
    except Exception as e:
        print(f"[markdown error] {e}", file=sys.stderr)
        return None

    try:
        client = OpenAI()
        run = client.beta.threads.create_and_run(
            assistant_id="asst_DXFpBka8vb7unu6jifZOLh6q",
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"Here is your markdown text:\n\n{markdown}\n\n"
                            "Analyze and return the most adequate title, no more than four words."
                        )
                    }
                ]
            }
        )

        thread_id = run.thread_id
        run_id = run.id

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run_status.status in ["completed", "failed", "cancelled"]:
                break
            time.sleep(1)

        if run_status.status != "completed":
            print(f"[openai error] Run status: {run_status.status}", file=sys.stderr)
            return None

        thread_messages = client.beta.threads.messages.list(thread_id=thread_id)

        for message in thread_messages.data:
            if message.role == "assistant":
                return message.content[0].text.value.strip()

        return None

    except Exception as e:
        print(f"[openai error] {e}", file=sys.stderr)
        return None


# --- CLI entry point ---
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_title.py \"text about something\"")
        sys.exit(1)

    text = sys.argv[1]
    title = generate_title_from_text(text)

    if title:
        print(title)
    else:
        print("[error] No title generated.")

