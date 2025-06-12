from .base_screen import BaseScreen
import json
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from ..widgets.tree_widget import RecordTree
from ..widgets.log_widget import LoggerWidget
from textual.widgets import Markdown, Input, TextArea
from clio.core.state import app_state
from clio.utils.logging import log_message
from textual import events
from ..widgets.controls import BaselineControlsWidget, DynamicControlsWidget
from ...ui.widgets.move import MoveRecordWidget
from ...utils.openai import generate_title_ai
from ...db.ops import update_record_title
from ..widgets.dynamic_form import DynamicFormWidget 
from clio.utils.markdown_utils import render_markdown
from clio.db.ops import save_record_to_db, save_embeddings

##############################################################################################
####################################### CONTENT SCREEN #######################################
##############################################################################################

class ContentScreen(BaseScreen):
    """Screen for viewing and editing record content."""

    CSS_PATH = ["../main.css", "content.css"]

    def compose(self) -> ComposeResult:
        """Define the container structure."""
        yield Vertical(
            Horizontal(
                Container(Markdown(id="cnt-content-md", classes="content-md"),id="cnt-markdown-container", classes="markdown-container"),
                Vertical(
                    Container(id="dyn-form", classes="form-container"),
                    id="cnt-right-panel",
                ),
                id="cnt-top-section",
            ),
            Horizontal(
                Container(LoggerWidget(id="cnt-rich-log", classes="rich-log"),id="cnt-logger-container", classes="logger-container"),
                Container(id="cnt-controls1", classes="controls1"),
                Container(id="cnt-controls2", classes="controls2"),
                Container(id="cnt-controls3", classes="controls2"),
                id="cnt-bottom-section",
            ),
        )
    


    def on_key(self, event: events.Key) -> None:
        """Check dynamic keybindings and execute actions."""
        key = event.key.lower()

        if key in app_state.dynamic_bindings:
            action, description = app_state.dynamic_bindings[key]
            log_message(f"Executing: {description}", "info")
            action()
            event.stop()
            self.query_one("DynamicControlsWidget").refresh()



    def on_mount(self) -> None:
        """Mount widgets and watch for changes to the markdown content."""
        app_state.dynamic_bindings = {
            "e": (self.action_edit_record, "Edit content"),
            "q": (self.action_quit_screen, "Quit content screen"),
            "s": (self.action_save_to_db, "Save Buffer to DB"),
        }

        markdown_widget = self.screen.query_one("#cnt-content-md")
        markdown_widget.update(app_state.current_content_markdown)
        for css_class in list(markdown_widget.classes):  
            markdown_widget.remove_class(css_class)
        
        markdown_widget.add_class(app_state.current_render_class)
        log_message(f"Added {app_state.current_render_class}", "info")

        # ✅ Mount controls into right-side panel
        self.query_one("#cnt-controls1").mount(BaselineControlsWidget())
        self.query_one("#cnt-controls2").mount(DynamicControlsWidget())





##############################################################################################
############################### UPDATE STATE FROM DYNAMIC INPUT FORM #########################
##############################################################################################


    def update_state_from_form(self) -> None:
        """Extracts data from the form, updates state, regenerates Markdown, and removes the form."""

        log_message("✅ Updating state from form and closing form.", "info")

        # ✅ Locate the dynamic form widget (not just the container)
        form_widget = self.query_one("DynamicFormWidget", DynamicFormWidget)


        # ✅ Ensure schema is always a dictionary
        schema = app_state.current_schema
        if isinstance(schema, str):
            try:
                schema = json.loads(schema)
            except json.JSONDecodeError:
                log_message("❌ Error: Invalid JSON schema format.", "error")
                return

        header_fields = schema.get("header", [])
        if isinstance(header_fields, str):
            header_fields = [header_fields]  # Ensure always a list
        content_fields = schema.get("content", [])
        if isinstance(content_fields, str):
            content_fields = [content_fields]  # Ensure always a list

        # ✅ Ensure `app_state.current_content` exists
        if not app_state.current_content:
            log_message("❌ app_state.current_content is None. Cannot update.", "error")
            return

        updated_data = {}

        # ✅ Extract header fields
        for field in header_fields:
                input_widget = form_widget.query_one(f"#field-{field}", Input)
                updated_data[field] = input_widget.value  
                log_message(f"✅ Extracted header '{field}': {updated_data[field]}", "debug")
        # ✅ Extract content fields
        for field in content_fields:
                content_widget = form_widget.query_one(f"#content-{field}", TextArea)
                updated_data[field] = content_widget.text  
                log_message(f"✅ Extracted content '{field}': {updated_data[field]}", "debug")


        # ✅ Apply updates to `app_state.current_content`
        for key, value in updated_data.items():
            if key in app_state.current_content.header:
                app_state.current_content.header[key] = value
            elif key in app_state.current_content.content:
                app_state.current_content.content[key] = value
            else:
                log_message(f"⚠ Warning: Unknown key '{key}' in updated_data", "warning")

        log_message(f"✅ Updated app_state.current_content: {app_state.current_content.__dict__}", "debug")

        # ✅ Generate Markdown
        app_state.current_content_markdown = render_markdown(app_state.current_content)

        log_message(f"✅ New Markdown Output:\n{app_state.current_content_markdown}", "debug")

        # ✅ Refresh Markdown widget
        markdown_widget = self.query_one("#cnt-content-md")
        markdown_widget.update(app_state.current_content_markdown)
        log_message("✅ Markdown widget updated.", "info")


        # ✅ Remove the actual DynamicFormWidget (not just the container)
        log_message("✅ Removing DynamicFormWidget...", "info")
        form_widget.remove()

        # ✅ Restore original keybindings
        app_state.dynamic_bindings = {
            "e": (self.action_edit_record, "Edit Content"),
            "q": (self.action_quit_screen, "Quit Content Screen"),
            "s": (self.action_save_to_db, "Save New State to DB"),
        }

        log_message("✅ Keybindings restored to default.", "info")


##############################################################################################
######################################## Main ACTIONS ########################################
##############################################################################################


    def action_edit_record(self) -> None:
            """Action: Modify the selected record."""
            if not app_state.current_UUID:
                log_message("No record selected for editing.", "warning")
                return

            # ✅ Debugging: Check schema before loading form
            if not app_state.current_schema:
                log_message("Error: No schema available, form cannot be loaded.", "error")
                return

            # ✅ Mount the form widget
            log_message("Mounting DynamicFormWidget...", "info")
            form_widget = DynamicFormWidget()
            self.query_one("#dyn-form").mount(form_widget)
            app_state.dynamic_bindings = {
            "ctrl+s": (self.update_state_from_form, "Confirm and update buffer"),
                "escape": (self.action_discard_form, "Cancel"),
            }

    def action_quit_screen(self):
        self.app.pop_screen()  # That's it




    def action_discard_form(self) -> None:
        """Discards any changes and removes the DynamicFormWidget without saving."""

        log_message("❌ Discarding changes and unloading the form.", "info")

        # ✅ Locate the dynamic form widget (not just the container)
        form_widget = self.query_one("DynamicFormWidget", DynamicFormWidget)
        form_widget.remove()  # ✅ Remove the form widget
        log_message("✅ DynamicFormWidget removed.", "info")

        # ✅ Restore original keybindings
        app_state.dynamic_bindings = {
            "e": (self.action_edit_record, "Edit content"),
            "q": (self.action_quit_screen, "Quit content ccreen"),
            "s": (self.action_save_to_db, "Save buffer to DB"),
        }

        log_message("✅ Keybindings restored to default.", "info")


    def action_generate_title(self):
        """Generate a title using OpenAI and update the record in the database."""
        if not app_state.current_UUID:
            log_message("No record selected for AI title generation.", "warning")
            return

        new_title = generate_title_ai()
        if new_title:
            update_record_title(app_state.current_UUID, new_title)  # ✅ Update the database
            self.query_one(RecordTree).refresh_tree()  # ✅ Refresh tree to show the new title

    def action_generate_embedding(self):
        """Generate and store vector embeddings for the selected record."""
        if not app_state.current_UUID:
            log_message("No record selected for embedding generation.", "warning")
            return

        embedding = generate_embedding(app_state.current_UUID)
        if embedding:
            log_message(f"Embedding generated and stored.", "info")

############################################# SAVE ###########################################

    def action_save_to_db(self) -> None:
        """Saves the updated state in `app_state.current_content` to the database and updates UI."""

        log_message("📝 Saving updated state to the database...", "info")

        # ✅ Ensure we have content to save
        if not app_state.current_UUID:
            log_message("❌ Cannot save: No record selected.", "error")
            return
        if not app_state.current_content:
            log_message("❌ Cannot save: `app_state.current_content` is None.", "error")
            return

        # ✅ Check if a title is already set
        buffer_title = app_state.current_content.header.get("title") or app_state.current_content.header.get("name")

        if not buffer_title:
            log_message("🔍 No title found. Generating a new one...", "info")
            new_title = generate_title_ai()
            if new_title:
                update_record_title(app_state.current_UUID, new_title)  # ✅ Update the database
                app_state.current_content.header["title"] = new_title  # ✅ Update in-memory content
                log_message(f"✅ New title generated: {new_title}", "info")
        
        update_record_title(app_state.current_UUID, buffer_title)  # ✅ Update the database
        log_message(f"💾 Saving record embeddings {app_state.current_UUID}...", "info")  # ✅ Use `app_state.current_UUID`
        save_embeddings(app_state.current_content)  # ✅ Save embeddings

        log_message(f"✅ Record {app_state.current_UUID} saved with embeddings!", "info")  # ✅ Use `app_state.current_UUID`

        # ✅ Call the database save function
        success = save_record_to_db()
        if success:
            log_message(f"✅ Record saved successfully to DB for UUID: {app_state.current_UUID}", "info")

            # ✅ Refresh the Markdown widget to reflect saved changes
            markdown_widget = self.query_one("#cnt-content-md")
            markdown_widget.update(app_state.current_content_markdown)
            log_message("✅ Markdown widget updated after save.", "info")
        else:
            log_message("❌ Error saving record to database.", "error")

