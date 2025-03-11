from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Static, Input
from clio.core.state import app_state
from clio.db.ops import save_appendix_entry_to_db  
from clio.utils.logging import log_message
from clio.utils.markdown_utils import render_markdown
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.containers import Container
from textual.widgets import Static, Input

##############################################################################################
######################## OVERLAY FOR APPENDICES WITH THREE CHILDREN ##########################
##############################################################################################
##############################################################################################

class AppendixScreen(Screen):
    """Parent class for all appendix entry screens."""

    BINDINGS = [("ctrl+enter", "confirm", "Confirm"), ("escape", "cancel", "Cancel")]

    def __init__(self, appendix_type, fields):
        """
        Initialize the appendix screen.
        
        Args:
            appendix_type (str): "note", "source", or "url".
            fields (dict): Field names mapped to their placeholders.
        """
        super().__init__()
        self.appendix_type = appendix_type
        self.inputs = {
            field: Input(placeholder=placeholder, classes="expand form-textfield")
            for field, placeholder in fields.items()
        }

    def compose(self):
        """Compose the screen layout."""
        popup = Container(
            *self.inputs.values(),
            classes="appendix-selector",
        )
        popup.border_title=f"Add {self.appendix_type.capitalize()} to the Record"
        popup.border_subtitle="[Ctrl+Enter] Confirm    [Esc] Cancel"
        yield popup

    def on_mount(self):
        """Focus the first input field when the screen is loaded."""
        first_input = next(iter(self.inputs.values()))
        first_input.focus()

    def action_confirm(self):
        """Confirm the appendix addition: update state, save to DB, and refresh UI."""
        data = {field: input_field.value.strip() for field, input_field in self.inputs.items()}

        # ✅ Validate input: Ensure all required fields are filled
        if not all(data.values()):
            log_message(f"⚠ Warning: All fields must be filled for {self.appendix_type}.", "warning")
            self.app.pop_screen()
            return

        log_message(f"✅ Adding {self.appendix_type}: {data}", "info")

        # ✅ Ensure the appendix exists in `app_state`
        if not hasattr(app_state.current_content, "appendix"):
            app_state.current_content.appendix = {}

        if self.appendix_type not in app_state.current_content.appendix:
            app_state.current_content.appendix[self.appendix_type] = []

        app_state.current_content.appendix[self.appendix_type].append(data)

        # ✅ Fix: Pass `data` as a dictionary, not unpacked
        if save_appendix_entry_to_db(self.appendix_type, data):  # ✅ Corrected
            log_message(f"✅ {self.appendix_type.capitalize()} successfully saved to database.", "info")
        else:
            log_message(f"❌ Error saving {self.appendix_type} to database.", "error")

        # ✅ Refresh Markdown
        app_state.current_content_markdown = render_markdown(app_state.current_content)

        # ✅ Close the overlay first
        self.app.pop_screen()

        # ✅ Update Markdown in the correct screen
        try:
            active_screen = self.app.screen  # ✅ Now refers to the correct active screen
            if hasattr(active_screen, "query_one"):
                markdown_widget = active_screen.query_one("#dash-content-md")
                markdown_widget.update(app_state.current_content_markdown)
                log_message("✅ Markdown widget updated.", "info")
            else:
                log_message("⚠ Warning: No active screen found to update markdown.", "warning")

        except NoMatches:
            log_message("❌ No Markdown widget found with ID '#dash-content-md'!", "error")

    def action_cancel(self):
        """Safely cancel and close the appendix screen."""
        log_message("❌ Appendix addition canceled.", "info")

        # ✅ Ensure the screen is still active before dismissing
        if self in self.app.screen_stack:
            self.dismiss()
        else:
            log_message("⚠ Warning: Tried to dismiss AppendixScreen but it's already gone.", "warning")


######################################### CHILDREN #############################################

# ✅ Child classes for specific appendix types
class AppendixNoteScreen(AppendixScreen):
    """Screen for adding a note appendix."""
    def __init__(self):
        super().__init__("note", {"note": "Enter your note here..."})


class AppendixSourceScreen(AppendixScreen):
    """Screen for adding a source appendix."""
    def __init__(self):
        super().__init__(
            "source",
            {
                "name": "Source Name",
                "type": "Source Type (book, article, etc.)",
                "author": "Author",
                "year": "Year",
            }
        )


class AppendixURLScreen(AppendixScreen):
    """Screen for adding a URL appendix."""
    def __init__(self):
        super().__init__(
            "url",
            {
                "title": "URL Title",
                "url": "Enter URL",
            }
        )

