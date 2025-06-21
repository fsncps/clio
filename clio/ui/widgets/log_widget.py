from textual.widgets import RichLog
from textual.widgets import Input, Static
from textual.containers import Horizontal, Vertical

class LoggerWidget(RichLog):
    """A widget for displaying application logs in real-time."""

    instance = None  # Singleton instance tracking

    def __init__(self, **kwargs):
        super().__init__(highlight=True, markup=True, auto_scroll=True, wrap=True, **kwargs)
        LoggerWidget.instance = self  # Track the instance

    def write_log(self, content: str):
        """Append log content to the logger."""
        self.write(content)


class ClioConsole(Vertical):
    """A console widget with a logger display and command input."""
    # CSS_PATH = ["console.css"]

    def compose(self):
        yield Vertical(
                LoggerWidget(id=f"{self.id}-log", classes="logger"),
                Horizontal(
                    Static("",classes="PS1"),
                    Input(placeholder="Enter command...", id=f"{self.id}-input", classes="prompt"),      classes="prompt-line"),
                classes="console")

    def on_mount(self):
        self.logger = self.query_one(f"#{self.id}-log", expect_type=LoggerWidget)
        self.input = self.query_one(f"#{self.id}-input", expect_type=Input)
        self.input.focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        from ...utils.log_util import log_message
        command = event.value.strip()
        if command:
            message = f"command `{command}` not found"
            log_message(message)
            self.logger.write_log(f"[b red]{message}[/]")
        self.input.value = ""
