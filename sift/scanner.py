import os 
import time
from pathlib import Path

from . import config
from .logger import get_logger

log = get_logger("sift")


def is_excluded(dir_name):
    return dir_name.lower() in config.EXCLUDED_DIRS


def scan_folder(root):
    """Walk throught the root and yeild one dict per file found."""
    root = Path(root)

    for current_dir, subdirs, filenames in os.walk(root):
        # Exclude certain directories
        subdirs[:] = [d for d in subdirs if not is_excluded(d)]

        for filename in filenames:
            full_path = Path(current_dir) / filename

            #skip files that are still downloading or temporary
            if full_path.suffix.lower() in config.TEMP_SUFFIXES:
                continue

            try:
                info = full_path.stat()
            except OSError as error:
                log.warning("Could not read file %s (%s)", full_path, error)
                continue

            yield {
                "path": str(full_path),
                "name": full_path.name,
                "extension": full_path.suffix.lower(),
                "size_bytes": info.st_size,
                "modified_at": info.st_mtime,
                "accessed_at": info.st_atime,
            }


def scan_and_save(conn, root):
    """Scan a folder and store every file in the database."""
    now = time.time()
    rows = []

    for rec in scan_folder(root):
        rows.append((
            rec["path"],
            rec["name"], 
            rec["extension"],
            rec["size_bytes"],
            rec["modified_at"],
            rec["accessed_at"],
            now,
        ))

    conn.executemany(
        """
        INSERT INTO files
            (path, name, extension, size_bytes, modified_at, accessed_at, scanned_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(path) DO UPDATE SET
            name = excluded.name,
            extension = excluded.extension,
            size_bytes = excluded.size_bytes,
            modified_at = excluded.modified_at,
            accessed_at = excluded.accessed_at,
            scanned_at = excluded.scanned_at
        """,
        rows,
    )
    conn.commit()
    return len(rows)


def top_largest(conn, limit=10):
    """Return the biggest files in the database."""
    cursor = conn.execute(
        "SELECT path, size_bytes FROM files ORDER BY size_bytes DESC LIMIT ?",
        (limit,),
    )
    return cursor.fetchall()

        
