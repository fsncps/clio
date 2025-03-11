from textual.app import App
from clio.ui.screens.dashboard import DashboardScreen

class ClioApp(App):
    """Main entry point for Clio Textual UI."""

    TITLE = "Clio"
    CSS_PATH = "main.css"

    async def on_mount(self):
        self.install_screen(DashboardScreen(), name="dashboard")
        await self.push_screen("dashboard")

if __name__ == "__main__":
    ClioApp().run()

