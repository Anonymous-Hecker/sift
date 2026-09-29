# Sift — WORKING.md

Living plan for the Stardance "Frictionless" project. Update this file at the end of every milestone.

**Platform:** Windows 10 Pro · **Target effort:** ~55 hours · **Commit + devlog cadence:** every 3-5 hours

---

## 1. Problem

- Files pile up with generic names (`image (14).png`, `IMG_0032.jpg`, `document(3).pdf`, `Screenshot ....png`), so nothing can be found later.
- The main disk fills up while other drives sit nearly empty. Windows Storage Sense only clears temp files and the recycle bin. It never moves anything and never explains itself.

## 2. Three major QoL improvements

1. **Content-aware renaming.** Sift reads what is inside a file and proposes a meaningful name. Only generic names are touched.
2. **Smart storage engine.** Scans all drives, ranks big/cold files, proposes moves to a roomier drive. Every move needs user approval, and the old path keeps working through a stub.
3. **Autopilot with a safety net.** New downloads are sorted by rules, duplicates are caught, and every action is journaled so it can be undone in one click.

## 3. Safety principles (built first, non-negotiable)

- **Dry-run by default.** Nothing changes on disk until the user approves.
- **Journal everything.** Every rename/move is written to SQLite *before* it happens. Undo reads the journal.
- **Verified moves.** Copy, hash both sides, verify, only then delete the source. Roll back on any mismatch.
- **Never touch:** `C:\Windows`, `Program Files`, `AppData`, system/hidden files, anything in a user-defined exclusion list.
- **Skip in-use and incomplete files:** `.crdownload`, `.part`, `.tmp`, locked files (handle `PermissionError`), and files still growing.
- **Never overwrite.** On a name clash, append a suffix.
- **Cloud placeholders** (OneDrive "online-only" files) are skipped, not downloaded.
- **Privacy:** all analysis is local by default. Any cloud AI is opt-in with a clear warning.

## 4. How it works

### Content-aware renamer
1. **Generic-name detector** (regex): `image (n)`, `IMG_####`, `Screenshot ...`, `download`, `untitled`, `document(n)`, `WhatsApp Image ...`.
2. **Extract content:**
   - PDF / DOCX / TXT: text and title/headings.
   - Images: OCR first; optional local vision model when there is no text.
3. **Name generation:** keywords or a small local LLM produce a 3-6 word slug plus a date if one is found.
4. **Confidence score:** high confidence renames automatically (after the user opts in); low confidence goes to a review queue.

### Storage engine
1. Scan all fixed drives into a SQLite index (path, size, mtime, atime, type).
2. **Move score** = size × time since last use × cold-type weight (videos, archives, installers, old project folders).
3. Build a plan: "Move 42 GB (18 files) from C: to D:, freeing X% of C:".
4. On approval: copy, hash-verify, delete original, leave a stub (`.lnk` for files, junction for folders).
5. Extras: duplicate finder, run-once installers (`.exe`/`.msi`), stale `node_modules`, monthly health report.

**Windows caveats to test early:**
- NTFS last-access updates can be disabled. Check with `fsutil behavior query disablelastaccess`, and fall back to modified time.
- Symlinks need elevated permissions, so use `.lnk` shortcuts and junctions instead.
- Handle long paths and locked files.

## 5. Stack

| Layer | Choice |
|---|---|
| Core engine | Python 3.11+, `watchdog`, SQLite, `pypdf`, `python-docx` |
| OCR | RapidOCR (ONNX, no separate install) |
| Local AI (optional) | Ollama small model / CLIP-style tagging |
| API | FastAPI |
| Dashboard | React (Vite) inside a `pywebview` window |
| Packaging | PyInstaller |
| Tests | `pytest` |

## 6. Repo layout

```
sift/
├─ WORKING.md
├─ README.md
├─ pyproject.toml
├─ sift/
│  ├─ config.py          # settings, exclusions
│  ├─ db.py              # SQLite schema + helpers
│  ├─ journal.py         # operation log + undo
│  ├─ fsops.py           # safe move/rename/copy-verify
│  ├─ watcher.py         # download watcher
│  ├─ rules.py           # rules engine (YAML)
│  ├─ scanner.py         # drive scan + index
│  ├─ extract/           # pdf, docx, txt, ocr
│  ├─ namer.py           # generic detector + name generator
│  ├─ storage/           # scoring, planner, mover, stubs
│  ├─ dupes.py
│  └─ api.py             # FastAPI
├─ ui/                   # React dashboard
└─ tests/
```

## 7. Milestones (each = one commit + one devlog)

| # | Hours | Milestone | Commit message idea |
|---|---|---|---|
| M1 | 3 | Repo scaffold, config, logging, SQLite schema, scanner v0 | `feat: project scaffold and basic drive scanner` |
| M2 | 4 | Journal + undo core, dry-run mode | `feat: operation journal with undo and dry-run` |
| M3 | 4 | Safe fs ops (never-overwrite, locked-file handling) + file watcher with debounce | `feat: safe file ops and download watcher` |
| M4 | 4 | Rules engine (YAML) + auto-sorter | `feat: rules engine and auto-sort` |
| M5 | 4 | Generic-name detector + PDF/DOCX/TXT extraction | `feat: generic name detection and text extraction` |
| M6 | 5 | OCR pipeline for images/screenshots | `feat: OCR pipeline for images` |
| M7 | 4 | Name generator, confidence scoring, review queue | `feat: content-based rename with review queue` |
| M8 | 4 | Multi-drive scan, atime check, large/old file index | `feat: multi-drive index of large and cold files` |
| M9 | 5 | Move scoring + move-plan builder | `feat: storage scoring and move planner` |
| M10 | 5 | Verified mover + `.lnk`/junction stubs + rollback | `feat: verified file mover with stubs and rollback` |
| M11 | 4 | Duplicate finder + installer/`node_modules` cleanup | `feat: duplicate and clutter detection` |
| M12 | 5 | FastAPI layer over all features | `feat: REST API` |
| M13 | 5 | React dashboard (storage map, rename queue, undo history) | `feat: dashboard UI` |
| M14 | 3 | Tests, packaging, README, demo video | `chore: packaging, docs and demo` |

**Total: 59 hours** (M6 and M13 are the likely overruns; trim M11 if time is short).

## 8. Devlog template (post after every milestone)

```
### Devlog #N — <milestone title> (<hours> hrs)

**What I built:**
- ...

**What changed since last time:**
- ...

**Problems I hit and how I solved them:**
- ...

**What's next:**
- ...

Commit: <link>
```

## 9. Definition of done

- Installer runs on a clean Windows 10 machine.
- Demo: a messy folder gets renamed and sorted live, a storage plan is approved and executed, and undo restores everything.
- README explains the problem, the 3 QoL wins, install steps and known limitations.
- Tests cover the journal, safe fs ops, the generic-name detector and the move planner.

## 10. Log

| Date | Milestone | Hours | Notes |
|---|---|---|---|
| | | | |
