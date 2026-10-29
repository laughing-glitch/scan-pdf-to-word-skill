"""Inspect dependencies or install Python packages into a private cache venv."""
import argparse
import importlib.util
import importlib.metadata
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import venv
from common import cache_dir, digest, emit, executable

MODULES = {"docx": "python-docx", "pypdfium2": "pypdfium2", "PIL": "Pillow"}
VERSION_RANGES = {"python-docx": ((1, 2), (2, 0)), "pypdfium2": ((4, 30), (6, 0)), "Pillow": ((11, 0), (13, 0))}
LANGUAGE_SHA256 = {
    "eng": "7d4322bd2a7749724879683fc3912cb542f19906c83bcc1a52132556427170b2",
    "chi_tra": "529c5b5797d64b126065cd55f2bb4c7fd7b15790798091b1ff259941a829330b",
    "chi_sim": "a5fcb6f0db1e1d6d8522f39db4e848f05984669172e584e8d76b6b3141e1f730",
}


def incompatible_packages():
    missing = []
    for module, package in MODULES.items():
        try:
            installed = importlib.metadata.version(package)
            parts = re.match(r"(\d+)\.(\d+)", installed)
            version = tuple(map(int, parts.groups())) if parts else (0, 0)
            low, high = VERSION_RANGES[package]
            if importlib.util.find_spec(module) is None or not low <= version < high:
                missing.append(package)
        except importlib.metadata.PackageNotFoundError:
            missing.append(package)
    return missing


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--install", action="store_true", help="Install missing Python packages in a cache venv")
    p.add_argument("--download-languages", action="store_true", help="Download official eng/chi_tra/chi_sim Tesseract data")
    p.add_argument("--cache-dir", type=Path, default=cache_dir())
    a = p.parse_args()
    a.cache_dir = a.cache_dir.expanduser().resolve()
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required. Use your agent's bundled Python if available.")
    missing = incompatible_packages()
    python = Path(sys.executable)
    if a.install and missing:
        target = a.cache_dir / "venv"
        python = target / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        if not python.exists():
            venv.EnvBuilder(with_pip=True).create(target)
        subprocess.run([str(python), "-m", "pip", "install", "-r",
                        str(Path(__file__).resolve().parents[1] / "requirements.txt")], check=True)
        subprocess.run([str(python), "-c", "import docx,pypdfium2,PIL"], check=True)
        missing = []
    downloaded = []
    if a.download_languages:
        target = a.cache_dir / "tessdata"
        target.mkdir(parents=True, exist_ok=True)
        for lang in ("eng", "chi_tra", "chi_sim"):
            path = target / (lang + ".traineddata")
            if not path.exists():
                url = f"https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/{lang}.traineddata"
                with urllib.request.urlopen(url, timeout=60) as response:
                    data = response.read(25 * 1024 * 1024)
                if not (100000 < len(data) < 25 * 1024 * 1024):
                    raise ValueError(f"Unexpected traineddata size: {lang}")
                pending = path.with_suffix(".download")
                pending.write_bytes(data)
                if digest(pending) != LANGUAGE_SHA256[lang]:
                    raise ValueError(f"Language file checksum mismatch: {lang}; download retained for inspection")
                pending.replace(path)
            if digest(path) != LANGUAGE_SHA256[lang]:
                raise ValueError(f"Cached language file checksum mismatch: {path}")
            downloaded.append({"language": lang, "sha256": digest(path)})
    emit({"python": str(python), "missing_or_incompatible_python_packages": missing,
          "tesseract": executable("tesseract"), "soffice": executable("soffice"),
          "apple_vision_available": sys.platform == "darwin" and bool(executable("swift")),
          "tessdata_dir": str(a.cache_dir / "tessdata"), "language_downloads": downloaded,
          "next": "Use the reported Python for all scripts. OCR and page rendering are optional helpers; visual review is still required."})
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
