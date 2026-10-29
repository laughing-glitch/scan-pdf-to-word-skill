"""Render with a detected LibreOffice and PDFium; keep QA files separate from the Word."""
import argparse
from pathlib import Path
import subprocess
import tempfile
from common import emit, executable, fresh_directory
from pdf_pages import render


def render_word(source, output, dpi=140, soffice=None):
    binary = soffice or executable("soffice")
    if not binary:
        raise ValueError("LibreOffice not found. Use the host's document renderer or references/setup.md. Do not claim visual QA passed.")
    dest = fresh_directory(output)
    with tempfile.TemporaryDirectory(prefix="scan-word-lo-") as profile:
        command = [str(binary), "-env:UserInstallation=" + Path(profile).as_uri(), "--headless",
                   "--convert-to", "pdf", "--outdir", str(dest), str(Path(source).resolve())]
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
    pdf = dest / (Path(source).stem + ".pdf")
    if completed.returncode != 0 or not pdf.is_file():
        raise ValueError(f"LibreOffice conversion failed: {completed.stdout}\n{completed.stderr}")
    manifest = render(pdf, dest / "pages", dpi)
    return {"pdf": str(pdf), "pages": len(manifest["pages"]), "images": str(dest / "pages"), "visual_review": "required"}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("docx", type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--dpi", type=int, default=140)
    p.add_argument("--soffice", help="Explicit executable path, including a host-bundled renderer")
    a = p.parse_args()
    emit(render_word(a.docx, a.out, a.dpi, a.soffice))
