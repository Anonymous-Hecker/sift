import sys
from pathlib import Path

from . import db, scanner


def main():
    """Main entry point for the command line interface."""
    if len(sys.argv) < 3 or sys.argv[1] != "scan":
        print("Usage: sift scan <folder>")
        return

    folder = Path(sys.argv[2])
    if not folder.is_dir():
        print(f"Error: {folder} is not a valid folder.")
        return

    conn = db.connect()
    db.init_db(conn)

    count = scanner.scan_and_save(conn, folder)
    print(f"Scanned {count} files in {folder}")

    print("Largest files:")
    for row in scanner.top_largest(conn, 10):
        size_mb = row["size_bytes"] / (1024 * 1024)
        print(f"{size_mb:10.1f} MB - {row['path']}")


if __name__ == "__main__":
    main()
