


from sift import db, fsops, journal


def make_db(tmp_path):
    (tmp_path / "data").mkdir()
    conn = db.connect(tmp_path / "data" / "test.db")
    db.init_db(conn)
    return conn


def test_apply_then_undo_restores_the_file(tmp_path):
    conn = make_db(tmp_path)
    folder = tmp_path / "files"
    folder.mkdir()
    original = folder / "image (1).png"
    renamed = folder / "chem-notes.png"
    original.write_text("pretend image")

    batch = journal.new_batch_id()
    journal.plan_move(conn, original, renamed, batch)

    journal.apply_batch(conn, batch, dry_run=False)
    assert renamed.exists()
    assert not original.exists()

    journal.undo_batch(conn, batch, dry_run=False)
    assert original.exists()
    assert not renamed.exists()
    assert original.read_text() == "pretend image"


def test_dry_run_changes_nothing(tmp_path):
    conn = make_db(tmp_path)
    folder = tmp_path / "files"
    folder.mkdir()
    original = folder / "a.txt"
    renamed = folder / "b.txt"
    original.write_text("hello")

    batch = journal.new_batch_id()
    journal.plan_move(conn, original, renamed, batch)
    journal.apply_batch(conn, batch, dry_run=True)

    assert original.exists()
    assert not renamed.exists()
    status = conn.execute("SELECT status FROM operations").fetchone()["status"]
    assert status == "planned"


def test_never_overwrites_an_existing_file(tmp_path):
    conn = make_db(tmp_path)
    folder = tmp_path / "files"
    folder.mkdir()
    a = folder / "a.txt"
    b = folder / "b.txt"
    a.write_text("A")
    b.write_text("B")

    batch = journal.new_batch_id()
    journal.plan_move(conn, a, b, batch)
    journal.apply_batch(conn, batch, dry_run=False)

    status = conn.execute("SELECT status FROM operations").fetchone()["status"]
    assert status == "failed"
    assert a.read_text() == "A"
    assert b.read_text() == "B"


def test_system_folders_are_protected():
    assert fsops.is_protected("C:\\Windows\\System32\\notepad.exe")
    assert not fsops.is_protected("C:\\Users\\someone\\Downloads\\a.txt")