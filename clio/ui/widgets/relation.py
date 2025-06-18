from textual.widget import Widget
from ...db.ops import fetch_content
from ...utils.markdown_utils import render_markdown
from textual.reactive import reactive
from textual.containers import Container
from textual.app import ComposeResult
from textual.widgets import Static
from clio.core.state import app_state
from clio.utils.log_util import log_message
from ...db.db import get_db
from sqlalchemy.sql import text
from ..widgets.tree_widget import RecordTree
from ...ui.screens.modal.selector import RelTypeSelector
from textual.widgets import DataTable
from textual.message import Message
from textual.reactive import reactive
from ...db.ops import fetch_relations_for_record  # Assume this exists
from textual.events import Key
# from textual.widgets import OptionList, Input
# from textual.widgets.option_list import Option

class NewRelationWidget(Widget):
    """Widget to select a related record and push relation type selection."""

    source_UUID = reactive("")
    source_name = reactive("")
    target_UUID = reactive(None)

    def __init__(self, source_uuid: str, source_name: str):
        super().__init__()
        self.source_UUID = source_uuid
        self.source_name = source_name
        self.target_UUID = None

        app_state.dynamic_bindings = {
            "l": (self.confirm_relation, "Confirm Relation"),
            "q": (self.cancel_relation, "Cancel Relation"),
        }

    def compose(self) -> ComposeResult:
        yield Container(
            Static(
                f"## Create Relation\n\n**{self.source_name}**\n\n"
                "Navigate to the related record using the tree.\n"
                "Press **[r]** again to select relation type, or **[q]** to cancel.",
                id="relation-instructions"
            ),
            id="relation-container"
        )

    def confirm_relation(self):
        """Select second record and push reltype selector screen."""
        try:
            tree = self.screen.query_one(RecordTree)
            selected_node = tree.cursor_node

            if selected_node and selected_node.data:
                self.target_UUID = selected_node.data.get("UUID")

            if not self.target_UUID or self.target_UUID == self.source_UUID:
                log_message("Invalid or same record selected. Relation cancelled.", "warning")
                return

            # Push relation type selector with a callback
            self.app.push_screen(RelTypeSelector(
                source_uuid=self.source_UUID,
                target_uuid=self.target_UUID
            ))


            self.remove()

        except Exception as e:
            log_message(f"❌ Error selecting related record: {e}", "error")



    def cancel_relation(self):
        log_message("Relation creation cancelled.", "info")
        self.remove()
        self.reset_bindings()

    def reset_bindings(self):
        if hasattr(self.screen, "define_dynamic_controls"):
            self.screen.define_dynamic_controls()

#############################################################################
### Relation List Widget#####################################################

class RelationListWidget(DataTable):
    current_uuid: reactive[str | None] = reactive(None)

    def __init__(self) -> None:
        super().__init__()
        self.add_columns("↔", "Name", "Type", "Description")
        self.relations: list[dict] = []

    def set_uuid(self, uuid: str) -> None:
        self.current_uuid = uuid
        self.refresh_table()

    def refresh_table(self) -> None:
        self.clear()
        self.relations = []

        if not self.current_uuid:
            return

        self.relations = fetch_relations_for_record(self.current_uuid)
        for rel in self.relations:
            self.add_row(
                rel["direction"],
                rel["target_name"],
                rel["reltype_label"],
                rel["description"] or "",
            )

    def on_key(self, event: Key) -> None:
        if event.key == "enter" and self.cursor_row is not None:
            if 0 <= self.cursor_row < len(self.relations):
                target_id = self.relations[self.cursor_row]["target_id"]
                log_message(f"[RelationList] Enter pressed. Switching to UUID: {target_id}", "info")
                app_state.current_UUID = target_id

                content_instance = fetch_content(target_id)
                if content_instance:
                    markdown = render_markdown(content_instance)
                    app_state.current_content_markdown = markdown
                    from ...ui.screens import content_screen
                    self.app.push_screen(content_screen.ContentScreen())  # type: ignore
                else:
                    log_message(f"No content found for {target_id}", "warning")


    # def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
    #     self.post_message(self.RelationSelected(self, target_id=event.row_key))

