"""Create OCR drafts, never final proofread text. Supports Tesseract and macOS Vision."""
import argparse
import csv
import io
from pathlib import Path
import subprocess
import sys
from common import cache_dir, emit, executable, fresh_directory, read_json, write_json


def tesseract_page(binary, image, languages, tessdata=None):
    command = [binary, str(image), "stdout", "-l", languages, "--psm", "3"]
    if tessdata:
        command += ["--tessdata-dir", str(tessdata)]
    command += ["tsv"]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=True, timeout=180)
    lines = {}
    for word in csv.DictReader(io.StringIO(result.stdout), delimiter="\t"):
        if not (word.get("text") or "").strip():
            continue
        key = tuple(word[k] for k in ("page_num", "block_num", "par_num", "line_num"))
        lines.setdefault(key, []).append({"text": word["text"], "confidence": float(word["conf"]),
                                         "box": [int(word[k]) for k in ("left", "top", "width", "height")]})
    return [{"text": " ".join(w["text"] for w in words), "words": words} for words in lines.values()]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("manifest", type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--engine", choices=["auto", "vision", "tesseract"], default="auto")
    p.add_argument("--languages", default="chi_tra+eng", help="Tesseract language codes")
    p.add_argument("--vision-languages", default="zh-Hant,en-US")
    p.add_argument("--tessdata", type=Path)
    a = p.parse_args()
    manifest = read_json(a.manifest)
    engine = a.engine
    if engine == "auto":
        engine = "vision" if sys.platform == "darwin" and executable("swift") else "tesseract"
    binary = executable("swift" if engine == "vision" else "tesseract")
    if not binary or (engine == "vision" and sys.platform != "darwin"):
        raise SystemExit(f"{engine} is unavailable. Read references/setup.md, or use the host's image-reading tool.")
    dest = fresh_directory(a.out)
    if engine == "vision":
        subprocess.run([binary, str(Path(__file__).with_name("vision.swift")),
                        str(a.manifest.resolve()), str(dest), a.vision_languages], check=True)
    else:
        tessdata = a.tessdata
        cached = cache_dir() / "tessdata"
        if tessdata is None and all((cached / (x + ".traineddata")).exists() for x in a.languages.split("+")):
            tessdata = cached
        for page in manifest["pages"]:
            image = a.manifest.resolve().parent / page["image"]
            regions = tesseract_page(binary, image, a.languages, tessdata)
            write_json(dest / f"page-{page['source_page']:04d}.json",
                       {"source_page": page["source_page"], "engine": engine, "regions": regions})
    drafts = []
    for page in manifest["pages"]:
        value = read_json(dest / f"page-{page['source_page']:04d}.json")
        drafts.append(f"=== SOURCE PAGE {page['source_page']} ===\n" + "\n".join(x["text"] for x in value["regions"]))
    (dest / "draft.txt").write_text("\n\n".join(drafts), encoding="utf-8")
    emit({"engine": engine, "pages": len(drafts), "draft": str(dest / "draft.txt"),
          "proofread": False, "notice": "Compare every source page. OCR confidence is not a correctness guarantee."})


if __name__ == "__main__":
    main()
