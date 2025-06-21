from clio.core.screen import ClioScreen
from ..widgets.content_md import HeaderDataWidget, ContentDataWidget  # adjust path as needed
from textual.containers import Vertical

from pathlib import Path
from ...utils.css_loader import load_css_from

class DetailsScreen(ClioScreen):
    """Details screen showing header data for a record."""

    CSS_PATH = [*load_css_from("../ui/css", Path(__file__).parent)]

    def load_record(self):
        """Load header and content widgets into main content area."""
        container = self.query_one(f"#{self.get_id('main-content')}")
        container.mount(
            Vertical(
                HeaderDataWidget(id="header-widget"),
                ContentDataWidget(id="content-widget"),
                id="details-content-layout", classes="details-container"
            )
        )

