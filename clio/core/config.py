import yaml
import os

# Ensure the config file is always found, no matter where the script is executed from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Directory of this script
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")  # Full path to config.yaml

def load_config(file_path=CONFIG_PATH):
    """Load configuration from a YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found at: {file_path}")

    with open(file_path, "r") as file:
        return yaml.safe_load(file)

