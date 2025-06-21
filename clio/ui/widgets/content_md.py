from textual.widgets import Markdown
from textual.containers import Vertical
from textual.widget import Widget
from clio.core.state import app_state
from clio.utils.markdown_utils import extract_markdown_parts


class HeaderDataWidget(Widget):
    def compose(self):
        yield Vertical(
                Markdown("", id="header-markdown", classes="header-md"),
                classes="header-md-container")

    def on_mount(self):
        self.md = self.query_one("#header-markdown", expect_type=Markdown)
        self.update_content()  # ✅ Only call now that self.md is set

    def update_content(self):
        content = app_state.current_content
        if content:
            parts = extract_markdown_parts(content)
            self.md.update(parts.header)
        else:
            self.md.update("*No content loaded*")


class ContentDataWidget(Widget):
    def compose(self):
        yield Vertical(
                Markdown("", id="content-markdown", classes="content-md"),
                classes="content-md-container")

    def on_mount(self):
        self.md = self.query_one("#content-markdown", expect_type=Markdown)
        self.update_content()  # ✅ Only call now that self.md is set

    def update_content(self):
        content = app_state.current_content
        if content:
            parts = extract_markdown_parts(content)
            self.md.update(parts.main)  # ✅ this was wrongly set to `parts.header`
        else:
            self.md.update("*No content loaded*")

