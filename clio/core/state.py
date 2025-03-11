from typing import Dict, Any
from textual.reactive import reactive
from textual.app import App
from .config import load_config

class ClioState(App):
    """Global state with schema, markdown rendering settings, and collections."""

    config = load_config()

    # Record metadata
    current_UUID = reactive(None)  # UUID of the active record
    current_rectype = reactive(None)  # Name of the record type
    current_schema = reactive[Dict[str, Any]]({})  # Explicit typing
    current_record_name = reactive("")  # The name of the record

    # Record content
    current_content = reactive(None)  # Dynamic class object from schema
    current_render_class = reactive("default")  # Specifies markdown styling class
    current_content_markdown = reactive("")  # Markdown extracted from the content object

    dynamic_bindings = {}

    _instance = None  # Singleton instance

    @classmethod
    def get_instance(cls):
        """Returns the single instance of ClioState."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Create and export the single instance
app_state = ClioState.get_instance()

__all__ = ["app_state"]
