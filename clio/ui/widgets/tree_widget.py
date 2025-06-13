from textual.widgets import Tree
from textual.widgets.tree import TreeNode
from textual.reactive import reactive
from ...db.ops import fetch_tree_data, fetch_content
from clio.utils.markdown_utils import render_markdown  # Import the updated tree data fetch
from rich.text import Text
from clio.core.state import app_state
from clio.utils.log_util import log_message
from rich.style import Style
from textual.widgets import Tree
from textual.events import Key



class RecordTree(Tree):
    """Tree widget that displays genus and record hierarchy."""

    CSS_PATH = "tree.css"

    def __init__(self, screen):
        self.data = fetch_tree_data()  # Fetch the data (genera and records)
        screen = screen
        super().__init__("Records")  # Set the correct root label
        self.populate_tree()  # Populate the tree with data
        self.selected_node = None  # Keep track of the selected node
        self.show_root = False
        self.show_guides = False

    def on_key(self, event):
        """Customize key behavior."""
        if event.key == "enter":
            # Select the current node but do NOT expand or collapse
            self.action_select_cursor()
            self.action_toggle_node()
            event.stop()  # Prevent default expansion behavior

    def refresh_tree(self):
        """Refresh the tree by clearing and repopulating it with updated data."""
        self.clear()  # ✅ Remove all existing nodes
        self.data = fetch_tree_data()  # ✅ Re-fetch updated data from the database
        self.populate_tree()  # ✅ Rebuild the tree
        self.refresh(layout=True)  # ✅ Ensure UI updates


    def key_right(self) -> None:
        """Expand current node on →"""
        node = self.cursor_node
        if node and not node.is_expanded and node.allow_expand:
            node.expand()

    def key_left(self) -> None:
        """Collapse current node on ←"""
        node = self.cursor_node
        if node and node.is_expanded:
            node.collapse()

    def render_label(self, node, base_style: Style, style: Style) -> Text:
        """Render a label while preserving expand/collapse icons and applying genus styles."""

        data = node.data or {}
        rectype = data.get("rectype", "default")
        node_type = data.get("type", "record")  # "genus" or "record"

        # Preserve expand/collapse icons
        icon = self.ICON_NODE_EXPANDED if node.is_expanded else self.ICON_NODE

        # Define Rich style mapping
        style_map = {
            "topic": Style(color="#eed49f", bold=True),  # Light gold color for topics
            "genus": Style(color="#ff8000", bold=True),  # Light red/pink for genus
            "default": Style(color="#cad3f5"),
        }

        # Extract text from Rich `Text` object
        raw_label = node.label.plain if isinstance(node.label, Text) else str(node.label)

        # Apply genus styling if this is a genus node
        if node_type == "genus":
            node_style = style_map["genus"]
            label_text = f"{raw_label.upper()}"  # ✅ Convert to uppercase
        else:
            node_style = style_map.get(rectype, style_map["default"])
            label_text = f"{icon}{raw_label}"  # Normal text for records


        # Apply special effects to the selected node
        if node == self.cursor_node:
            node_style = Style(color="green", bold=True)  # Selected is bold green

        # selected node style
        if node.data and node.data.get("selected", False):
            node_style = node_style + Style(bold=True)  # Or use color/background

        # Preserve Textual cursor/highlight effects
        full_style = base_style + style + node_style  

        # Render the label with all styles
        return Text(label_text, style=full_style)

    def populate_tree(self):
        """Recursively build the tree structure from the database, with each genus as a separate root."""
        self.clear()  # Ensure we start fresh

        record_nodes = {}
        records_by_parent = {}

        for record in self.data["records"]:
            parent_id = record["parent_UUID"]
            if parent_id not in records_by_parent:
                records_by_parent[parent_id] = []
            records_by_parent[parent_id].append(record)

        def add_records(parent_node: TreeNode, parent_id):
            """Recursively add records under the given parent node."""
            if parent_id not in records_by_parent:
                return  # No children for this parent

            for record in records_by_parent[parent_id]:
                record_icon = record.get("icon", " ")  
                record_name = record.get("name", "Unnamed")
                render_class = record.get("content_render_class", "default")  # ✅ Get class from DB



                rectype = record.get("rectype", "default")
                if rectype == "topic":
                    label_text = f"{record_icon}   {record_name}"  # ✅ Extra spacing for topics
                else:
                    label_text = f"{record_icon} {record_name}"  # Default format

                # ✅ Apply the class as text style instead of set_class()
                record_label = label_text
                node = parent_node.add(record_label)  # ✅ Assign styled text to node
                # ✅ Store record data
                node.data = {
                    "UUID": record["UUID"],
                    "icon": record_icon,
                    "name": record_name,
                    "rectype": record["rectype"],
                    "content_schema": record["content_schema"],
                    "content_caption": record["content_caption"],
                    "content_render_class": render_class,
                    "type": "record",
                }


                record_nodes[record["UUID"]] = node
                add_records(node, record["UUID"])  # Recursively add child records

        for genus in self.data["genera"]:
            genus_name = genus["name"]

            # ✅ Assign genus label with Nerd Font icon
            genus_label = Text(f"󰩳  {genus_name}", style="bold yellow")

            genus_node = self.root.add(genus_label)

            genus_node.data = {
                "UUID": genus["UUID"],
                "name": genus["name"],
                "description": genus["description"],
                "genus_type_id": genus["genus_type_id"],
                "type": "genus",
            }

            add_records(genus_node, genus["UUID"])  # Populate genus-level records

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle node selection, update state, and apply selection styling."""
        selected_node: TreeNode = event.node

        # Get data from the selected node
        if not selected_node or not hasattr(selected_node, "data") or selected_node.data is None:

            log_message(f"Dropping out with {selected_uuid}", "info")    
            return

        node_data = selected_node.data
        selected_uuid = node_data.get("UUID")

        # Log selection
        log_message(f"Selected UUID: {selected_uuid}", "info")    

        if selected_uuid:
            if node_data["type"] == "record":  # ✅ Handle record selection
                # Update AppState with record data
                app_state.current_UUID = selected_uuid
                app_state.current_rectype = node_data.get("rectype")
                app_state.current_render_class = node_data.get("content_render_class")
                app_state.current_content_caption = node_data.get("content_caption")
                app_state.current_schema = node_data.get("content_schema")
                app_state.current_record_name = node_data.get("name")
                app_state.current_content_markdown: reactive[str | None] = reactive("")  # Reset content markdown for now
                
                # Fetch content based on the current UUID, rectype, and schema
                content_instance = fetch_content(selected_uuid)

                if content_instance:
                    log_message(f"Fetched content for {selected_uuid}: {content_instance.content}", "info")
                    markdown = render_markdown(content_instance)
                    app_state.current_content_markdown = markdown
                    log_message(f"Rendered Markdown for {app_state.current_rectype} {selected_uuid}", "info")
                else:
                    log_message(f"Failed to fetch content for {selected_uuid}", "warning")

            elif node_data["type"] == "genus":  # ✅ Handle genus selection
                log_message(f"Selected genus: {node_data['name']}", "info")

                # Render genus information as markdown
                genus_markdown = f"# {node_data['name']}\n\n{node_data['description']}"
                app_state.current_content_markdown = genus_markdown
                app_state.current_render_class = "default-markdown"

            # Reset styles by traversing all nodes
            def reset_styles(node: TreeNode):
                if isinstance(node.label, Text):
                    node.label.stylize("white")  # Reset to default
                for child in node.children:
                    reset_styles(child)

            reset_styles(self.root)

            # Apply selected style
            if isinstance(selected_node.label, Text):
                selected_node.label.stylize("bold green")
                log_message(f"app_state.current_UUID: {app_state.current_UUID}", "info")
                log_message(f"app_state.current_rectype: {app_state.current_rectype}", "info")
                log_message(f"app_state.current_schema: {app_state.current_schema}", "info")
                log_message(f"app_state.current_record_name: {app_state.current_record_name}", "info")
                log_message(f"app_state.current_content: {app_state.current_content}", "info")
                log_message(f"app_state.current_UUID: {app_state.current_render_class}", "info")
                log_message(f"app_state.current_content_markdown: {app_state.current_content_markdown}", "info")



            self.refresh(layout=True)

