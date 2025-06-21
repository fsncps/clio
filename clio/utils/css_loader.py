from pathlib import Path
import os

def load_css_from(folder: str, relative_to: Path) -> list[str]:
    """Return all .css file paths in folder, relative to the importing module's path."""
    css_dir = (Path(__file__).parent / folder).resolve()
    return [
        os.path.relpath(str(p), start=relative_to)
        for p in css_dir.glob("*.css")
    ]

