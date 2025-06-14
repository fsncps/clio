from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Static
from textual import events
from typing import Callable

from .baseline_popup import PopupScreen

##############################################################################################
########################### Confirmation Modal for Deletions etc. ############################

class ConfirmationScreen(Screen):
    """A full-screen confirmation overlay that locks interactions."""
    def __init__(self, message: str, on_confirm: Callable):
        super().__init__(classes="popup-screen")
        self.message = message
        self.on_confirm = on_confirm


    BINDINGS = [("y", "confirm", "Confirm"), ("n", "cancel", "Cancel")]




    def compose(self):
        """Compose the screen with a full-screen background and centered confirmation box."""
        yield Container(
            Static(self.message, id="confirm-message"),
            Static("[y] Yes    [n] No", id="confirm-options"),
            id="confirm-box",
        )

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard input: 'y' to confirm, 'n' to cancel."""
        if event.key == "y":
            self.on_confirm()
            self.app.pop_screen()  # Close the confirmation screen
        elif event.key == "n":
            self.app.pop_screen()  # Close the screen without action

