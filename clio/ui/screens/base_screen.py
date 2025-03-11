from textual.screen import Screen
from clio.core.state import app_state

class BaseScreen(Screen):
    """Base screen with shared state and utility functions."""

    def on_mount(self):
        """Ensure each screen has access to the current record."""
        self.current_UUID = app_state.current_UUID
        self.loaded_content = app_state.current_content

