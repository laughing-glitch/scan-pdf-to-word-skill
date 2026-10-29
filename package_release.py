"""Create an importable skill ZIP and a starter ZIP without local job data."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parent


def source_files():
    allowed_roots = {"skills", "docs", "examples", "tests", ".github"}
    allowed_root_files = {"README.md", "LICENSE", ".gitignore", "install.sh", "install.ps1",
                          "install-windows.cmd", "install-mac.command", "package_release.py"}
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(x in rel.parts for x in ("__pycache__", ".venv", "work", "dist", ".git")):
            continue
        if rel.parts[0] in allowed_roots or (len(rel.parts) == 1 and path.name in allowed_root_files):
            if path.suffix in (".pyc", ".traineddata", ".pdf", ".docx"):
                continue
            yield path, rel


def build():
    dest = ROOT / "dist"
    dest.mkdir(exist_ok=True)
    paths = list(source_files())
    for name, skill_only in (("scan-pdf-to-word.zip", True), ("scan-pdf-to-word-starter.zip", False)):
        with zipfile.ZipFile(dest / name, "w", zipfile.ZIP_DEFLATED) as z:
            if skill_only:
                z.write(ROOT / "LICENSE", "scan-pdf-to-word/LICENSE")
            for path, rel in paths:
                if skill_only:
                    if rel.parts[:2] != ("skills", "scan-pdf-to-word"):
                        continue
                    arc = Path(*rel.parts[1:])
                else:
                    arc = Path("scan-pdf-to-word-skill") / rel
                z.write(path, arc.as_posix())
    checks = []
    for path in sorted(dest.glob("*.zip")):
        checks.append(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name)
    (dest / "SHA256SUMS.txt").write_text("\n".join(checks) + "\n", encoding="utf-8")
    print("\n".join(checks))


if __name__ == "__main__":
    build()
