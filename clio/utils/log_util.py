from loguru import logger
import os
import sys
from ..ui.widgets.log_widget import LoggerWidget

# ✅ Get the correct project root directory
base_dir = os.path.dirname(os.path.abspath(__file__))  
log_file = os.path.join(base_dir, "logs", "clio.log") 

# 🔍 Debug: Print the resolved log file path
print(f"[DEBUG] Resolved log file path: {log_file}")

# ✅ Ensure logs directory exists
try:
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    print(f"[DEBUG] Ensured log directory exists: {os.path.dirname(log_file)}")
except Exception as e:
    print(f"[ERROR] Failed to create log directory: {e}")

# ✅ Remove existing handlers
logger.remove()
print("[DEBUG] Removed existing Loguru handlers.")

# ✅ Add file handler (without enqueue=True for now)
logger.add(log_file, rotation="10MB", level="DEBUG")
print(f"[DEBUG] Added Loguru file handler to: {log_file}")

# ✅ Add a test log entry to confirm it's writing
logger.debug("[DEBUG] Log system initialized.")

def log_message(content: str, level="info"):
    """Logs messages to file, updates LoggerWidget, and prints debugging info."""

    level_styles = {
        "info": "[cyan]",
        "warning": "[yellow]",
        "error": "[red bold]"
    }

    styled_message = f"{level_styles.get(level, '[white]')}[{level.upper()}] {content}[/]"

    # 🔍 Debug: Print what is being logged
    print(f"[DEBUG] Logging message: {content} (Level: {level})")

    # ✅ Log to file
    if level == "info":
        logger.info(content)
    elif level == "warning":
        logger.warning(content)
    elif level == "error":
        logger.error(content)

    # ✅ Ensure LoggerWidget receives formatted messages
    if LoggerWidget.instance and "sqlalchemy" not in content.lower():
        LoggerWidget.instance.write(styled_message)
        print("[DEBUG] LoggerWidget updated.")

def get_logger():
    """Returns the global logger instance for importing."""
    return logger

# ✅ Final debugging: Print logger handlers
print(f"[DEBUG] Active Loguru handlers: {logger}")
print(f"[DEBUG] Log file exists: {os.path.exists(log_file)}")

