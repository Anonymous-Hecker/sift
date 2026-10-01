from pathlib import Path

# Sift keeps its own database and logs in an hidden folder -> home directory
APP_DIR = Path.home() / ".sift"
DB_PATH = APP_DIR / "sift.db"
LOG_PATH = APP_DIR / "sift.log"

# Strictly OFF LIMIT Folders
EXCLUDED_DIRS = {
    "windows",
    "program files",
    "proram files (x86)",
    "programdata",
    "appdata",
    "$recycle.bin",
    "system volume information",
}

# Ignoring these files
TEMP_SUFFIXES = {".crdownload", ".part", ".tmp", ".partial"}

# Top-level Windows folders that Sift refuses to touch, ever
PROTECTED_TOP_LEVEL = {
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "$recycle.bin",
    "system volume information",
}


def ensure_app_dir():
    """Creating the .sift folder if it dosen't exist"""
    APP_DIR.mkdir(parents=True, exist_ok=True)




