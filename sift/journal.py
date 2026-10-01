
import time
import uuid

from . import fsops
from .logger import get_logger

log = get_logger()


def new_batch_id():
    """Make a short random ID that groups related operations together."""
    return uuid.uuid4().hex[:8]


def plan_move(conn, source, dest, batch_id):
    """Write a 'planned' row to the journal. This touches NO files."""
    cursor = conn.execute(
        """
        INSERT INTO operations
            (batch_id, op_type, source_path, dest_path, status, created_at)
        VALUES (?, 'move', ?, ?, 'planned', ?)
        """,
        (batch_id, str(source), str(dest), time.time()),
    )
    conn.commit()
    return cursor.lastrowid


def _finish(conn, op_id, status, error=None):
    """Record how an operation ended."""
    conn.execute(
        "UPDATE operations SET status = ?, error = ?, finished_at = ? WHERE id = ?",
        (status, error, time.time(), op_id),
    )
    conn.commit()


def apply_batch(conn, batch_id, dry_run=True):
    """Carry out every planned operation in a batch. Returns how many worked."""
    rows = conn.execute(
        "SELECT * FROM operations WHERE batch_id = ? AND status = 'planned' ORDER BY id",
        (batch_id,),
    ).fetchall()

    moved = 0
    for row in rows:
        if dry_run:
            print(f"[dry-run] would move {row['source_path']} -> {row['dest_path']}")
            continue

        try:
            fsops.safe_move(row["source_path"], row["dest_path"])
        except fsops.FsOpError as error:
            _finish(conn, row["id"], "failed", str(error))
            log.error("Move failed: %s", error)
            print(f"FAILED: {error}")
        else:
            _finish(conn, row["id"], "done")
            log.info("Moved %s -> %s", row["source_path"], row["dest_path"])
            print(f"moved {row['source_path']} -> {row['dest_path']}")
            moved += 1

    return moved


def undo_batch(conn, batch_id, dry_run=True):
    """Reverse every finished operation in a batch. Returns how many worked."""
    rows = conn.execute(
        "SELECT * FROM operations WHERE batch_id = ? AND status = 'done' ORDER BY id DESC",
        (batch_id,),
    ).fetchall()

    undone = 0
    for row in rows:
        if dry_run:
            print(f"[dry-run] would move back {row['dest_path']} -> {row['source_path']}")
            continue

        try:
            fsops.safe_move(row["dest_path"], row["source_path"])
        except fsops.FsOpError as error:
            log.error("Undo failed: %s", error)
            print(f"COULD NOT UNDO: {error}")
        else:
            _finish(conn, row["id"], "undone")
            log.info("Undid %s", row["id"])
            print(f"moved back {row['dest_path']} -> {row['source_path']}")
            undone += 1

    return undone


def last_batch_id(conn):
    """The most recent batch that still has something to undo."""
    row = conn.execute(
        "SELECT batch_id FROM operations WHERE status = 'done' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row["batch_id"] if row else None


def recent_history(conn, limit=20):
    cursor = conn.execute(
        "SELECT * FROM operations ORDER BY id DESC LIMIT ?", (limit,)
    )
    return cursor.fetchall()




