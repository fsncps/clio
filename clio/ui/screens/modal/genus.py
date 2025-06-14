from sqlalchemy import text
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Input, Select
from textual.app import ComposeResult
from ....db.db import engine
from ....core.genus import GenusDB
from .baseline_popup import PopupScreen

class GenusPopup(PopupScreen):
    """Popup for adding or editing a genus."""
    BINDINGS = [
        ("ctrl+s", "confirm", "Confirm"),
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, mode="create", genus_data=None):
        """
        Initialize the genus popup.
        :param mode: "create" or "edit"
        :param genus_data: dict with existing genus info (for edit mode)
        """
        super().__init__(title="Genus Details")
        self.mode = mode
        self.genus_data = genus_data or {}
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
        yield from self.compose_popup(
            self.inputs["shortname"],
            self.inputs["longname"],
            self.select
        )


    def on_mount(self):
        """Focus the first input field and prefill if editing."""
        if self.mode == "edit" and self.genus_data:
            self.inputs["shortname"].value = self.genus_data.get("shortname", "")
            self.inputs["longname"].value = self.genus_data.get("longname", "")
            self.select.value = str(self.genus_data.get("type_id", ""))
        self.inputs["shortname"].focus()


    def action_confirm(self):
        """Create or update genus."""
        data = {field: input_field.value.strip() for field, input_field in self.inputs.items()}
        selected_genus_type = self.select.value

        if not all(data.values()) or self.select.is_blank():
            log_message("⚠ Warning: All fields must be filled.", "warning")
            return

        try:
            if not selected_genus_type.isdigit():
                raise ValueError(f"Invalid genus type ID: {selected_genus_type}")
            genus_type_id = int(selected_genus_type)

            if self.mode == "edit":
                from ...core.genus import GenusDB  # Adjust import
                GenusDB.update_genus(self.genus_data["uuid"], data["shortname"], data["longname"], genus_type_id)
                log_message(f"✏️ Genus updated: {data}", "info")
            else:
                genus_id = GenusDB.create_genus(data["shortname"], data["longname"], genus_type_id)
                log_message(f"✅ Genus added: {data} (ID: {genus_id})", "info")

        except Exception as e:
            log_message(f"❌ Error saving genus: {e}", "error")

        self.app.pop_screen()



    @staticmethod
    def update_genus(uuid: str, shortname: str, longname: str, type_id: int):
        query = text("""
            UPDATE genus SET shortname = :shortname, longname = :longname, genus_type_id = :type_id
            WHERE uuid = :uuid
        """)
        with engine.connect() as conn:
            conn.execute(query, {"uuid": uuid, "shortname": shortname, "longname": longname, "type_id": type_id})
            conn.commit()


def log_message(message, level="info"):
    """Placeholder logging function."""
    print(f"[{level.upper()}] {message}")


