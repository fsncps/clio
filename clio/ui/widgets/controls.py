from textual.widgets import Static
from rich.table import Table
from textual.reactive import reactive
from clio.core.state import app_state
from clio.utils.logging import log_message

##############################################################################################
################################# Static Baseline Widget #####################################

class BaselineControlsWidget(Static):
    """A widget to display baseline controls in a clean, two-column layout."""

    DEFAULT_CSS = """
    BaselineControls {
        background: #1e1e1e;
        color: white;
        border: solid gray;
        padding: 3 1 1 1;
        width: 100%;
        height: auto;
        align: left top;
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update(self.render_controls())

    def render_controls(self) -> Table:
        """Generate and return the baseline controls as a two-column table."""
        # Create a Rich Table
        table = Table.grid(padding=(0, 2))  # Add padding between columns
        table.add_column("Key", style="bold yellow", no_wrap=True)
        table.add_column("Action", style="white")

        # Add rows of baseline controls
        controls = [
            ("Tab/S-Tab", "Move focus"),
            ("←↑↓→", "Navigate"),
            ("Space", "Expand/Collapse"),
            ("Enter", "Select Record"),
            ("", ""),
            ("Q", "Quit"),
        ]

        for key, action in controls:
            table.add_row(key, action)

        return table

##############################################################################################
########################## Dynamic Widget for Context Controls ###############################


class DynamicControlsWidget(Static):
    """A widget to display dynamic keybindings in a two-column layout."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dynamic_bindings = reactive(dict(app_state.dynamic_bindings))  # ✅ Copy bindings reactively
        self.update(self.render())  # ✅ Initial render

    def watch_dynamic_bindings(self, old_value, new_value):
        """Trigger a re-render whenever the keybindings change."""
        self.update(self.render())  # ✅ Re-render table

    def render(self) -> Table:
        """Generate and return the dynamic controls as a two-column table."""
        table = Table.grid(padding=(0, 2))
        table.add_column("Key", style="bold cyan", no_wrap=True)
        table.add_column("Action", style="white")

        # ✅ Populate from `app_state.dynamic_bindings`
        for key, (_, description) in app_state.dynamic_bindings.items():
            table.add_row(f"[bold]{key.upper()}[/]", description)

        return table

    def refresh_table(self):
        """Re-render controls when any widget is mounted."""
        self.update(self.render()) 


