from .base_screen import BaseScreen
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, Container
from ..widgets.tree_widget import RecordTree
from ..widgets.log_widget import LoggerWidget
# from ..widgets.content_widget import MarkdownDisplay
from textual.widgets import Markdown, Tree
from clio.core.state import app_state
from textual import events
# from ..widgets.content_widget import DynamicMarkdownViewer
from textual import on
from clio.utils.logging import log_message
from ..widgets.controls import BaselineControlsWidget, DynamicControlsWidget
from ..widgets.selector import RecordTypeSelector  # Import the new widget
from ...core.record import create_record
from ...core.record import recursive_delete
from ...ui.widgets.confirmation import ConfirmationScreen
from ...ui.widgets.move import MoveRecordWidget
from ...utils.openai import generate_title_ai
from ...db.ops import update_record_title
from ..widgets.selector import AppendixSelectorScreen
from ..widgets.genus_widget import GenusPopup
from ..widgets.remove_appendix import AppendixRemoveScreen

##############################################################################################
###################################### DASHBOARD SCREEN ######################################
##############################################################################################

class DashboardScreen(BaseScreen):
    """Main dashboard layout with empty containers for widgets."""

    CSS_PATH = ["../main.css", "dashboard.css"]

    def compose(self) -> ComposeResult:
        """Define the container structure."""
        yield Vertical(
            Horizontal(
                Container(id="dash-tree-container", classes="tree-container"),
                Container(Markdown(id="dash-content-md", classes="content-md"),id="dash-markdown-container", classes="markdown-container"),  
                id="dash-top-section",
            ),
            Horizontal(
                Container(LoggerWidget(id="dash-rich-log", classes="rich-log"),id="dash-logger-container"),
                Container(id="dash-controls1", classes="controls1"),
                Container(id="dash-controls2", classes="controls1"),
                Container(id="dash-controls3", classes="controls1"),
                id="dash-bottom-section",
            ),
        )
   

    def on_screen_resume(self):
        self.query_one(RecordTree).refresh_tree()

    @on(Tree.NodeSelected)
    def update_markdown(self) -> None:
        markdown_widget = self.screen.query_one("#dash-content-md")
        markdown_widget.update(app_state.current_content_markdown)
        for css_class in list(markdown_widget.classes):  
            markdown_widget.remove_class(css_class)
        
        markdown_widget.add_class(app_state.current_render_class)
        log_message(f"Added {app_state.current_render_class}", "info")

    def on_key(self, event: events.Key) -> None:
        """Check dynamic keybindings and execute actions."""
        key = event.key.lower()

        if key in app_state.dynamic_bindings:
            action, description = app_state.dynamic_bindings[key]  # ✅ Retrieve function & description
            log_message(f"Executing: {description}", "info")  # ✅ Log what action is triggered
            action()  # ✅ Execute the function
            event.stop()  # ✅ Stop further event propagation
            self.query_one("DynamicControlsWidget").refresh()


    def on_mount(self) -> None:
        """Mount widgets and watch for changes to the markdown content."""
        app_state.dynamic_bindings = {
        "g": (self.action_add_genus, "Create New Genus"),
        "n": (self.action_add_record, "Create New Record"),
        "e": (self.action_edit_record, "Edit Selected Record"),
        "b": (self.action_generate_embedding, "Generate Embedding"),
        "d": (self.action_delete_record, "Delete Selected Record"),
        "m": (self.action_move_record, "Move Selected Record"),
        "c": (self.action_content_screen, "Content Screen"),
        "a": (self.action_add_appendix, "Add appendix"),
        "r": (self.action_remove_appendix, "Remove appendix"),

        }

        tree = RecordTree(screen=self)
        self.query_one("#dash-tree-container").mount(tree)

        # ✅ Ensure Markdown Viewer is mounted
        content_viewer = Markdown()
        self.query_one("#dash-markdown-container").mount(content_viewer)

        # ✅ Mount BaseControlsInfo in the "controls" container
        base_controls = BaselineControlsWidget()
        self.query_one("#dash-controls1").mount(base_controls)
        dyn_controls = DynamicControlsWidget()
        self.query_one("#dash-controls2").mount(dyn_controls)



##############################################################################################
###################################### APPENDICES ############################################

    def action_add_appendix(self) -> None:
        """Opens the Appendix Selector Screen to choose an appendix type."""
        self.app.push_screen(AppendixSelectorScreen())




    def action_add_note_appendix(self) -> None:
        self.app.push_screen(AppendixNoteScreen())

    def action_add_url_appendix(self) -> None:
        self.app.push_screen(AppendixURLScreen())
  
    def action_add_source_appendix(self) -> None:
        self.app.push_screen(AppendixSourceScreen())

    def action_remove_appendix(self) -> None:
        """Opens the Appendix Selector Screen to choose an appendix type."""
        self.app.push_screen(AppendixRemoveScreen())

##############################################################################################
############################## ADD / EDIT / DELETE RECORD ####################################
    def action_add_genus(self) -> None:
        """Action: Add a new record."""
        log_message("Adding a new genus..", "info")
        self.app.push_screen(GenusPopup())



    def action_add_record(self) -> None:
        """Action: Add a new record."""
        if app_state.current_UUID:
            log_message("Adding a new record...", "info")
            self.app.push_screen(RecordTypeSelector())
        else: log_message("No parent record selected.", "error")


    def action_edit_record(self) -> None:
        """Action: Modify the selected record."""
        create_record("note", app_state.current_UUID)
    
    def action_content_screen(self):
        """Switch to the Content Editor screen."""
        if not app_state.current_UUID:
            log_message("No record selected for editing.", "warning")
            return
        
        from .content_screen import ContentScreen
        self.app.push_screen(ContentScreen())  # ✅ Load the content screen


    def action_delete_record(self):
        """Triggered by a keybinding to delete a record."""
        if not app_state.current_UUID or not app_state.current_rectype:
            log_message("No record selected for deletion.", "warning")
            return  

        def confirm_deletion():
            recursive_delete(app_state.current_UUID)
            log_message(f"Deleted record: {app_state.current_UUID}", "info")

        # Push the confirmation screen
        self.app.push_screen(ConfirmationScreen("Delete this record? (y/n)", confirm_deletion))

##############################################################################################
#################################### VARIOUS ACTIONS #########################################

    def action_quit(self) -> None:
        """Action: Quit the application."""
        self.app.exit()

    def action_cancel(self) -> None:
        """Cancel operation and context state"""
        app_state.dynamic_bindings = {
        "n": (self.action_add_record, "Create New Record"),
        "e": (self.action_edit_record, "Edit Selected Record"),
        "b": (self.action_generate_embedding, "Generate Embedding"),
        "d": (self.action_delete_record, "Delete Selected Record"),
        "m": (self.action_move_record, "Delete Selected Record"),
        "t": (self.action_generate_title, "Generate Title"),
        "c": (self.action_content_screen, "Content Screen"),
        "a": (self.action_add_appendix, "Add appendix"),
        }



    def action_move_record(self):
        """Trigger the move record process."""
        if not app_state.current_UUID:
            log_message("No record selected to move.", "warning")
            return

        # Create and mount the move widget
        move_widget = MoveRecordWidget(app_state.current_UUID, app_state.current_record_name)
        self.query_one("#dash-controls2").mount(move_widget)

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

