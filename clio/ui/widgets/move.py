from textual.widget import Widget
from textual.reactive import reactive
from textual.containers import Container
from textual.app import ComposeResult
from textual import events
from textual.widgets import Static
from textual.widgets import Tree
from clio.core.state import app_state
from clio.utils.log_util import log_message
from textual import on
from ...db.db import get_db
from sqlalchemy.sql import text
from ...utils.queries import get_all_descendants
from ..widgets.tree_widget import RecordTree  # ✅ Import RecordTree


##############################################################################################
##################################### MOVE Record Widget #####################################

class MoveRecordWidget(Widget):
    """Widget to select a new parent for a record."""

    move_UUID = reactive("")  # UUID of the record being moved
    move_name = reactive("")  # Name of the record being moved
    new_parent_UUID = reactive(None)  # UUID of the new parent

    def __init__(self, record_uuid: str, record_name: str):
        super().__init__()
        self.move_UUID = record_uuid
        self.move_name = record_name
        self.new_parent_UUID = None  # No parent selected yet

        # Update keybindings to allow move confirmation
        app_state.dynamic_bindings = {
            "m": (self.confirm_move, "Confirm Move"),
            "q": (self.cancel_move, "Cancel Move"),
        }

    def compose(self) -> ComposeResult:
        """Render the move instructions as Markdown."""
        yield Container(
            Static(f"## Move Record\n\n**{self.move_name}**\n\n"
                   "Navigate to the new parent using the tree. Press **[m]** again to confirm, or **[q]** to cancel.",
                   id="move-instructions"),
            id="move-container"
        )

    def confirm_move(self):
        """Confirm and move the record after the user presses `m` again."""
        try:
            tree = self.screen.query_one(RecordTree)  # ✅ Get tree instance
            selected_node = tree.cursor_node  # ✅ Get selected node

            if selected_node and selected_node.data:
                self.new_parent_UUID = selected_node.data.get("UUID")

            if not self.new_parent_UUID:
                log_message("No valid parent selected. Move cancelled.", "warning")
                return

            # ✅ Prevent moving into its own descendant
            descendants = get_all_descendants(self.move_UUID)
            if self.new_parent_UUID in descendants:
                log_message("Error: Cannot move record into its own child.", "error")
                return

            # Move the record
            self.move_record(self.move_UUID, self.new_parent_UUID)

            # Remove widget after move
            self.remove()

            # Reset keybindings
            self.reset_bindings()

        except Exception as e:
            log_message(f"Error selecting parent for move: {e}", "error")

    def move_record(self, record_uuid: str, new_parent_uuid: str):
        """Update the record's parent UUID in the database."""
        with next(get_db()) as db:
            update_query = text("UPDATE record SET parent_UUID = :new_parent WHERE UUID = :record")
            db.execute(update_query, {"new_parent": new_parent_uuid, "record": record_uuid})
            db.commit()
            log_message(f"Record {record_uuid} moved under parent {new_parent_uuid}.", "info")

    def cancel_move(self):
        """Cancel the move operation."""
        log_message("Move operation cancelled.", "info")
        self.remove()
        self.reset_bindings()

    def reset_bindings(self):
        """Reset keybindings to default after move or cancel."""
        app_state.dynamic_bindings = {
            "n": (self.screen.action_add_record, "Create New Record"),
            "e": (self.screen.action_edit_record, "Edit Selected Record"),
            "d": (self.screen.action_delete_record, "Delete Selected Record"),
            "m": (self.screen.action_move_record, "Move Selected Record"),
        }

