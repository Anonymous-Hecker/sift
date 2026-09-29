from sift import db, scanner


def test_scan_finds_files_and_skips_excluded(tmp_path):
    # tmp_path is a fresh temporary folder that pytest creates for us
    files = tmp_path / "files"
    data = tmp_path / "data"
    files.mkdir()
    data.mkdir()

    (files / "a.txt").write_text("hello")
    (files / "movie.mp4").write_bytes(b"x" * 1000)
    (files / "video.crdownload").write_text("partial")
    (files / "AppData").mkdir()
    (files / "AppData" / "secret.txt").write_text("nope")

    conn = db.connect(data / "test.db")
    db.init_db(conn)

    count = scanner.scan_and_save(conn, files)

    names = {row["name"] for row in conn.execute("SELECT name FROM files")}
    assert count == 2
    assert names == {"a.txt", "movie.mp4"}