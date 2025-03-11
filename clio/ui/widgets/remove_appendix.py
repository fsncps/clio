from textual.screen import Screen
from textual.widgets import SelectionList, Static
from sqlalchemy.sql import text
from clio.core.state import app_state
from clio.utils.logging import log_message
from textual.css.query import NoMatches
from clio.db.db import get_db
from clio.utils.markdown_utils import render_markdown
from clio.db.ops import delete_from_database
from textual.screen import Screen
from textual.widgets import SelectionList, Static
from sqlalchemy.sql import text

##############################################################################################
################################ OVERLAY FOR SELECTION LIST ##################################
##############################################################################################
##############################################################################################

class AppendixRemoveScreen(Screen):
    """Screen for selecting and removing appendix entries."""
    
    BINDINGS = [("ctrl+enter", "confirm_removal", "Remove Selected"), ("esc", "cancel", "Cancel")]

    def __init__(self):
        """Initialize the screen with a selection list of appendix items."""
        super().__init__()
        self.selection_list = SelectionList()

    def compose(self):
        """Create the selection list and add appendix items."""
        yield Static("Select appendix items to remove:", classes="title")
        yield self.selection_list
        yield Static("[Ctrl+Enter] Remove Selected    [Esc] Cancel", classes="footer")

    def on_mount(self):
        """Populate the selection list when the screen is displayed."""
        log_message("📌 on_mount: Loading appendix items into selection list...", "debug")
        self.populate_selection_list()



##############################################################################################
################################### POPULATE SELECTION LIST ##################################

    def populate_selection_list(self):
        """Query all appendix items from the database and load them into the selection list."""
        log_message("📌 populate_selection_list: Querying database for appendices...", "debug")
        self.selection_list.clear_options()

        query = text("""
            SELECT UUID, note AS name, 'note' AS appendix_type FROM rec_note WHERE rec_UUID = :record_UUID
            UNION ALL
            SELECT UUID, CONCAT(name, ' (', COALESCE(author, 'Unknown'), ', ', COALESCE(CAST(year AS CHAR), 'Unknown'), ')') AS name, 'source' AS appendix_type FROM rec_source WHERE rec_UUID = :record_UUID
            UNION ALL
            SELECT UUID, CONCAT(title, ': ', url) AS name, 'url' AS appendix_type FROM rec_url WHERE rec_UUID = :record_UUID
        """)

        params = {"record_UUID": app_state.current_UUID}

        with next(get_db()) as db:
            results = db.execute(query, params).fetchall()

        log_message(f"📌 Retrieved {len(results)} appendices from database", "debug")

        for uuid, name, appendix_type in results:
            item_repr = f"[{appendix_type.capitalize()}] {name}"
            log_message(f"✅ Adding to selection list: {item_repr} (UUID: {uuid})", "debug")
            self.selection_list.add_option((item_repr, (appendix_type, uuid)))





##############################################################################################
################################### FORMAT SELECTION LIST ITEMS ##############################

    def format_appendix_item(self, appendix_type, item):
        """Format an appendix item for display in the selection list."""
        log_message(f"📌 format_appendix_item: Formatting {appendix_type}: {item} (Type: {type(item)})", "debug")

        # ✅ Correcting source and URL handling
        if appendix_type == "note":
            return f"[Note] {item}"  # ✅ Directly show note content

        elif appendix_type == "source":
            name = item.get("name")
            return f"[Source] {name}" if name else "[Source] (No Name)"

        elif appendix_type == "url":
            title = item.get("title")
            url = item.get("url")
            return f"[URL] {title}" if title else f"[URL] {url}" if url else "[URL] (No Title)"

        log_message(f"⚠ Unrecognized appendix type: {appendix_type}", "error")
        return "[Unknown]"



##############################################################################################
####################@@@@#### CONFIRM AND REMOVE FROM DB AND APP_STATE ########################

    def action_confirm_removal(self):
        """Remove selected appendix items."""
        selected_items = self.selection_list.selected  # List of (appendix_type, UUID) tuples

        if not selected_items:
            log_message("⚠ No items selected for removal.", "warning")
            return

        log_message(f"🗑 Removing {len(selected_items)} appendix items...", "info")

        for appendix_type, uuid in selected_items:
            log_message(f"📌 Removing {appendix_type} with UUID: {uuid}", "debug")
            
            # ✅ No need to convert UUIDs into dicts
            delete_from_database(appendix_type, uuid)  

        # Refresh UI
        app_state.current_content_markdown = render_markdown(app_state.current_content)
        self.app.pop_screen()

        # Update Markdown in active screen
        try:
            active_screen = self.app.screen
            if hasattr(active_screen, "query_one"):
                markdown_widget = active_screen.query_one("#dash-content-md")
                markdown_widget.update(app_state.current_content_markdown)
                log_message("✅ Markdown widget updated.", "info")
        except NoMatches:
            log_message("❌ No Markdown widget found with ID '#dash-content-md'!", "error")



    def remove_from_app_state(self, appendix_type, item):
        """Remove an appendix item from `app_state.current_content.appendix`."""
        appendix = getattr(app_state.current_content, "appendix", {})

        log_message(f"📌 remove_from_app_state: Removing {appendix_type}: {item}", "debug")

        if appendix_type in appendix and item in appendix[appendix_type]:
            appendix[appendix_type].remove(item)
            log_message(f"✅ Removed {appendix_type}: {item}", "info")

