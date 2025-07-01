# clio/config/install_config.py

import os
from pathlib import Path
import shutil

CONFIG_DIR = Path.home() / ".config" / "clio"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

files = {
    "telegram_secrets.env.template": "telegram_secrets.env",
    "telegram_gpg.asc": "telegram_gpg.asc",
}

for src, dst in files.items():
    src_path = Path(__file__).parent / src
    dst_path = CONFIG_DIR / dst
    if not dst_path.exists():
        shutil.copy(src_path, dst_path)
        print(f"Installed {dst}")
    else:
        print(f"Skipped {dst}, already exists")

