"""Small local-only helpers shared by the command-line tools."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys


def emit(value):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(value, ensure_ascii=False, indent=2))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fresh_directory(path):
    path = Path(path).resolve()
    if path.exists() and any(path.iterdir()):
        raise ValueError(f"Output directory is not empty; choose a new one: {path}")
    path.mkdir(parents=True, exist_ok=True)
    return path


def executable(name):
    override = os.environ.get("SCAN_PDF_TO_WORD_" + name.upper())
    if override:
        if Path(override).is_file():
            return override
        raise ValueError(f"Configured {name} does not exist: {override}")
    found = shutil.which(name)
    if found:
        return found
    candidates = []
    if name == "soffice":
        candidates.append("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    for variable in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        base = os.environ.get(variable)
        if base and name == "tesseract":
            candidates += [str(Path(base) / "Tesseract-OCR/tesseract.exe"),
                           str(Path(base) / "Programs/Tesseract-OCR/tesseract.exe")]
        if base and name == "soffice":
            candidates.append(str(Path(base) / "LibreOffice/program/soffice.exe"))
    return next((p for p in candidates if Path(p).is_file()), None)


def cache_dir():
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library/Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "scan-pdf-to-word"
