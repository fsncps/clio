from textual.widget import Widget
from textual.containers import Container, Horizontal
from textual.widgets import OptionList, Input, Select
from textual.widgets import OptionList, Button, Static
from textual.widgets.option_list import Option
from textual.app import ComposeResult
from textual.events import Key
from textual.message import Message
import uuid
from textual.screen import ModalScreen
from sqlalchemy.sql import text  # Import text for raw SQL execution
from ....core.record import create_record
from ....db.db import get_db
from clio.core.state import app_state
from clio.utils.log_util import log_message
from textual.app import ComposeResult
from .appendix import AppendixNoteScreen, AppendixURLScreen, AppendixSourceScreen
from typing import Callable
from .baseline_popup import PopupScreen

##############################################################################################
######################## OVERLAY FOR RECTYPE SELECTION FOR NEW RECORD ########################
##############################################################################################

class RecordTypeSelector(PopupScreen):
    """Popup to select a record type and create a new record."""
    def __init__(self):
        super().__init__(title="Select Record Type")

    def compose(self) -> ComposeResult:
        self.option_list = OptionList(id="rectype-options", classes="selection-list")
        self.option_list.border_title = "Select Record Type"

        yield from self.compose_popup(self.option_list)


    def on_mount(self):
        """Populate options when the screen loads."""
        self.populate_options()




##############################################################################################
################################### POPULATE OPTION LIST #####################################

    def populate_options(self):
        """Fetch record types and populate the option list."""
        record_types = self.get_record_types()
        if not record_types:
            log_message("⚠ Warning: No record types found!", "warning")
            return

        for rectype in record_types:
            self.option_list.add_option(rectype.capitalize())  # ✅ Add record type

        log_message(f"✅ Populated record types: {record_types}", "debug")

    def get_record_types(self):
        """Fetch available record types from the `rectype` table."""
        with next(get_db()) as db:
            result = db.execute(text("SELECT name FROM rectype"))
            tables = [row[0] for row in result]  # ✅ Store as lowercase for consistency
        return tables

    def on_key(self, event: Key) -> None:
        """Handle keyboard navigation and selection."""
        if event.key == "escape":
            log_message("❌ Record type selection canceled.", "info")
            self.dismiss()
        elif event.key == "enter":
            self.create_selected_record()

    def create_selected_record(self):
        """Create a new record from the selected type and close the popup."""
        selected_option = self.option_list.highlighted  # ✅ Get highlighted index

        if selected_option is not None:
            rectype = self.option_list.get_option_at_index(selected_option).prompt.lower()  # ✅ Normalize case
            log_message(f"✅ Creating record of type: {rectype}", "info")

            create_record(rectype, app_state.current_UUID)  # ✅ Create new record
            self.dismiss()

##############################################################################################
################################ OVERLAY FOR RELTYPE SELECTION ###############################
##############################################################################################


class RelTypeSelector(PopupScreen):
    """Popup to select a relation type and enter a description."""
    def __init__(self, source_uuid: str, target_uuid: str):
        super().__init__(title="Specify Relation")
        self.source_uuid = source_uuid
        self.target_uuid = target_uuid

    def compose(self):
        self.description_input = Input(placeholder="Optional description...", id="rel-desc")
        self.relation_select = Select(
            options=[],  # initially empty
            prompt="Select relation type",
            allow_blank=True,  # ← fix here
            id="reltype-select"
        )

        yield from self.compose_popup(self.description_input, self.relation_select)


    def on_mount(self):
        """Populate the select widget with relation types from DB."""
        with next(get_db()) as db:
            result = db.execute(text("SELECT name, id FROM reltype ORDER BY name"))
            options = [(name.capitalize(), int(reltype_id)) for name, reltype_id in result]
            self.relation_select.set_options(options)

            # Set default to ID 99 if it exists
            for label, value in options:
                if value == 99:
                    self.relation_select.value = 99
                    break


    def on_key(self, event: Key) -> None:
        if event.key == "escape":
            log_message("❌ Relation creation cancelled.", "info")
            self.dismiss()
        elif event.key == "enter":
            self.confirm_relation()

    def confirm_relation(self):
        """Confirm selection and insert the relation."""
        if self.relation_select.is_blank():
            log_message("⚠ No relation type selected.", "warning")
            return

        reltype_id = self.relation_select.value
        description = self.description_input.value.strip()

        new_uuid = str(uuid.uuid4())
        with next(get_db()) as db:
            db.execute(
                text("""
                    INSERT INTO relations (UUID, rec_UUID, rel_rec_UUID, reltype_id, description)
                    VALUES (:uuid, :rec, :rel, :reltype, :desc)
                """),
                {
                    "uuid": new_uuid,
                    "rec": self.source_uuid,
                    "rel": self.target_uuid,
                    "reltype": reltype_id,
                    "desc": description
                }
            )
            db.commit()

        log_message(f"✅ Created relation {self.source_uuid} --[{reltype_id}]--> {self.target_uuid}", "info")
        self.dismiss()

##############################################################################################
################################ OVERLAY FOR APPENDIX SELECTION ##############################
##############################################################################################

class AppendixSelectorScreen(PopupScreen):
    """Popup for selecting an appendix type to add to the current record."""
    def __init__(self):
        super().__init__(title="Select Appendix Type")

    def compose(self):
        """Create the UI layout with an OptionList and buttons."""
        log_message("🔍 Debug: Composing AppendixSelectorScreen...", "debug")

        self.option_list = OptionList(id="appendix-options", classes="selection-list")  # ✅ Ensure OptionList exists
        self.option_list.border_title="Select Appendix Type" 
        yield from self.compose_popup(self.option_list)
        
        # ✅ Ensures the OptionList is part of the UI
        # yield Container(
        #     Button("Confirm", id="confirm-button"),
        #     Button("Cancel", id="cancel-button"),
        #     id="button-container",
        # )

    def on_mount(self):
        """Populate options after the UI has loaded."""
        self.populate_options()

    def populate_options(self):
        """Fetch available appendix types and populate the option list."""
        appendix_types = self.get_available_appendices()

        if not appendix_types:
            log_message("⚠ Warning: No appendices available!", "warning")
            return

        for appendix in appendix_types:
            self.option_list.add_option(appendix.capitalize())  # ✅ Pass a plain string

        log_message(f"✅ Populated appendix options: {appendix_types}", "debug")

    def get_available_appendices(self):
        """Retrieve available appendix types from `current_schema`."""
        appendix_options = app_state.current_schema.get("appendix", [])

        if isinstance(appendix_options, str):
            appendix_options = [appendix_options]  # ✅ Convert to list if it's a string

        log_message(f"📜 Available appendices: {appendix_options}", "debug")
        return appendix_options if appendix_options else ["None"]

    def on_key(self, event: Key) -> None:
        """Handle keyboard navigation and selection."""
        if event.key == "escape":
            log_message("❌ Appendix selection canceled.", "info")
            self.dismiss()
        elif event.key == "enter":
            self.confirm_selection()



    def confirm_selection(self):
        """Open the corresponding appendix input screen."""
        selected_option = self.option_list.highlighted  # ✅ Get selected option

        if selected_option is not None:
            appendix_type = self.option_list.get_option_at_index(selected_option).prompt.lower()
            log_message(f"✅ Selected appendix type: {appendix_type}", "info")

            # ✅ Open the corresponding appendix input screen
            if appendix_type == "note":
                self.app.push_screen(AppendixNoteScreen())
            elif appendix_type == "source":
                self.app.push_screen(AppendixSourceScreen())
            elif appendix_type == "url":
                self.app.push_screen(AppendixURLScreen())
            else:
                log_message("⚠ Warning: No valid appendix selected.", "warning")


