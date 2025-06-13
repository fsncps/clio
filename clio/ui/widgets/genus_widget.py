from sqlalchemy import text
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Input, Select
from textual.app import ComposeResult
from ...db.db import engine
from ...core.genus import GenusDB

class GenusPopup(Screen):
    """Popup for adding a new genus."""
    BINDINGS = [
        ("ctrl+s", "confirm", "Confirm"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self):
        """
        Initialize the genus popup.
        """
        super().__init__()
        self.inputs = {
            "shortname": Input(placeholder="Short Name", classes="form-textfield"),
            "longname": Input(placeholder="Long Name", classes="form-textfield"),
        }
        self.select = Select(self.get_genus_types(), prompt="Select Genus Type")

    @staticmethod
    def get_genus_types():
        """Retrieve genus types from the database, ensuring valid integer IDs."""
        query = text("SELECT id, shortname FROM genus_type;")
        with engine.connect() as connection:
            result = connection.execute(query)
            return [(row[1], str(row[0])) for row in result.fetchall()]


    def compose(self) -> ComposeResult:
        """Compose the popup layout."""
        popup = Container(
            self.inputs["shortname"],
            self.inputs["longname"],
            self.select,
            classes="genus-popup",
        )
        popup.border_title = "Add New Genus"
        popup.border_subtitle = "Ctrl+Enter: Confirm    Esc: Cancel"
        yield popup

    def on_mount(self):
        """Focus the first input field when the screen is loaded."""
        self.inputs["shortname"].focus()

    def action_confirm(self):
        """Confirm the genus addition: validate input, save to DB, and refresh UI."""
        data = {field: input_field.value.strip() for field, input_field in self.inputs.items()}
        selected_genus_type = self.select.value

        if not all(data.values()) or self.select.is_blank():
            log_message("⚠ Warning: All fields must be filled.", "warning")
            return

        try:
            if not selected_genus_type.isdigit():
                raise ValueError(f"Invalid genus type ID: {selected_genus_type}")

            genus_type_id = int(selected_genus_type)

            genus_id = GenusDB.create_genus(data["shortname"], data["longname"], genus_type_id)
            log_message(f"✅ Genus added: {data} (ID: {genus_id})", "info")
        except ValueError as e:
            log_message(f"❌ Error: {e}", "error")
        except Exception as e:
            log_message(f"❌ Error adding genus: {e}", "error")

        self.app.pop_screen()


    def action_cancel(self):
        """Cancel and close the popup."""
        log_message("❌ Genus addition canceled.", "info")
        self.dismiss()


def log_message(message, level="info"):
    """Placeholder logging function."""
    print(f"[{level.upper()}] {message}")

