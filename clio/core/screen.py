# core/screen.py

from textual.screen import Screen
from textual.containers import Vertical, Horizontal, Container
from textual.widgets import Static, Input, Markdown
from clio.core.state import app_state
from ..ui.widgets.log_widget import LoggerWidget, ClioConsole
from ..ui.widgets.controls import BaselineControlsWidget, DynamicControlsWidget
from ..utils.log_util import log_message
from pathlib import Path
from ..utils.css_loader import load_css_from

class ClioScreen(Screen):
    """Base screen with shared layout, state access, logger, and input."""

    CSS_PATH = [*load_css_from("../ui/css", Path(__file__).parent)]
    BINDINGS = [("q", "app.pop_screen", "Close screen")]

    def compose(self):
        yield Vertical(
            Container(Markdown("# CLIO TITLE", id=self.get_id("title-bar"), classes="title-md"),classes="title-container"),

            Container(id=self.get_id("main-content"),classes="main-content"),

            Horizontal(
                Container(
                    ClioConsole(id=self.get_id("console"), classes="console-widget"),
                    id=self.get_id("console-container"), classes="console-container"
                ),
                Container(BaselineControlsWidget(id=self.get_id("stat-controls"), classes="stat-controls"),classes="stat-controls-container"),
                Container(DynamicControlsWidget(id=self.get_id("dyn-controls"), classes="dyn-controls"),classes="dyn-controls-container"),
                Container(Static("Hints and help", id=self.get_id("help-pane"),classes="help-pane"),classes="help-pane-container"),
                id=self.get_id("bottom-bar"), classes="bottom-bar"
            ),
            id=self.get_id("screen-root"),classes="screen-root"
        )


    def get_id(self, name: str) -> str:
        """Generate a namespaced ID for a widget."""
        return f"{self.__class__.__name__.lower()}-{name}"

    def on_mount(self):
        self.current_UUID = app_state.current_UUID
        self.current_content = app_state.current_content
        self.console = self.query_one(f"#{self.get_id('console')}", expect_type=ClioConsole)
        self.stat_controls = self.query_one(f"#{self.get_id('stat-controls')}", expect_type=BaselineControlsWidget)
        self.dyn_controls = self.query_one(f"#{self.get_id('dyn-controls')}", expect_type=DynamicControlsWidget)

        self.main_container = self.query_one(f"#{self.get_id('main-content')}", expect_type=Container)

        self.load_record()

    def load_record(self):
        """Override this method in subclass screens to populate content."""
        pass

