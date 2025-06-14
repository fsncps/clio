from textual.screen import ModalScreen
from textual.containers import Container
from textual.widgets import Static
from clio.utils.log_util import log_message
from textual.app import ComposeResult

class PopupScreen(ModalScreen):
    """Base for all modal popups with shared layout and behavior."""

    BINDINGS = [
        ("enter", "confirm", "Confirm"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, title: str = "", subtitle: str = ""):
        super().__init__(classes="popup-screen")
        self.popup_title = title
        self.popup_subtitle = subtitle

    def compose_popup(self, *widgets) -> ComposeResult:
        """Compose standard popup container layout."""
        popup = Container(*widgets, classes="modal-popup")
        popup.border_title = self.popup_title
        popup.border_subtitle = self.popup_subtitle or "Enter: Confirm    Esc: Cancel"
        yield Container(popup, id="modal-center")

    def action_cancel(self):
        """Default cancel behavior."""
        log_message("❌ Modal cancelled.", "info")
        self.dismiss()



