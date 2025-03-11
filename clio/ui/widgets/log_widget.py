from textual.widgets import RichLog

class LoggerWidget(RichLog):
    """A widget for displaying application logs in real-time."""

    instance = None  # Singleton instance tracking

    def __init__(self, **kwargs):
        super().__init__(highlight=True, markup=True, auto_scroll=True, wrap=True, **kwargs)
        LoggerWidget.instance = self  # Track the instance

    def write_log(self, content: str):
        """Append log content to the logger."""
        self.write(content)

