import argparse
from pathlib import Path

from . import db, fsops, journal, scanner


def cmd_scan(args):
    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"That is not a folder: {folder}")
        return

    conn = db.connect()
    db.init_db(conn)

    count = scanner.scan_and_save(conn, folder)
    print(f"Scanned {count} files in {folder}")

    print("Largest files:")
    for row in scanner.top_largest(conn, 10):
        size_mb = row["size_bytes"] / (1024 * 1024)
        print(f"{size_mb:10.1f} MB - {row['path']}")


def cmd_move(args):
    problem = fsops.check_move(args.source, args.dest)
    if problem:
        print(f"Refused: {problem}")
        return

    if not args.apply:
        print(f"[dry-run] would move {args.source} -> {args.dest}")
        print("Add --apply to really do it.")
        return

    conn = db.connect()
    db.init_db(conn)

    batch_id = journal.new_batch_id()
    journal.plan_move(conn, args.source, args.dest, batch_id)
    moved = journal.apply_batch(conn, batch_id, dry_run=False)
    if moved:
        print(f"Done (batch {batch_id}). Undo with: python -m sift undo --apply")


def cmd_history(args):
    conn = db.connect()
    db.init_db(conn)

    rows = journal.recent_history(conn, args.limit)
    if not rows:
        print("The journal is empty.")
        return

    for row in rows:
        print(
            f"#{row['id']:<4} {row['batch_id']} {row['status']:<8} "
            f"{row['source_path']} -> {row['dest_path']}"
        )


def cmd_undo(args):
    conn = db.connect()
    db.init_db(conn)

    batch_id = args.batch or journal.last_batch_id(conn)
    if batch_id is None:
        print("Nothing to undo.")
        return

    undone = journal.undo_batch(conn, batch_id, dry_run=not args.apply)
    if not args.apply:
        print("That was a dry run. Add --apply to really undo.")
    else:
        print(f"Undid {undone} operation(s) from batch {batch_id}.")


def main():
    parser = argparse.ArgumentParser(
        prog="sift", description="Sift: file management without friction"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="scan a folder into the database")
    p_scan.add_argument("folder")
    p_scan.set_defaults(func=cmd_scan)

    p_move = sub.add_parser("move", help="move a file (dry-run unless --apply)")
    p_move.add_argument("source")
    p_move.add_argument("dest")
    p_move.add_argument("--apply", action="store_true")
    p_move.set_defaults(func=cmd_move)

    p_history = sub.add_parser("history", help="show the journal")
    p_history.add_argument("--limit", type=int, default=20)
    p_history.set_defaults(func=cmd_history)

    p_undo = sub.add_parser("undo", help="undo the last batch (dry-run unless --apply)")
    p_undo.add_argument("--batch")
    p_undo.add_argument("--apply", action="store_true")
    p_undo.set_defaults(func=cmd_undo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()