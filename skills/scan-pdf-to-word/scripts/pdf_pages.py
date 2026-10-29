"""Render a PDF into numbered page images and a source manifest. Never edit the PDF."""
import argparse
from pathlib import Path
import pypdfium2 as pdfium
from common import digest, emit, fresh_directory, write_json


def page_selection(value, count):
    if not value:
        return list(range(1, count + 1))
    pages = set()
    for item in value.split(","):
        ends = item.strip().split("-")
        if len(ends) == 1:
            pages.add(int(ends[0]))
        elif len(ends) == 2:
            start, end = map(int, ends)
            if start > end:
                raise ValueError("Reversed page range")
            pages.update(range(start, end + 1))
        else:
            raise ValueError("Use page numbers/ranges such as 1,3-5")
    if not pages or min(pages) < 1 or max(pages) > count:
        raise ValueError(f"Page selection outside 1..{count}")
    return sorted(pages)


def render(source, output, dpi=300, selected=None):
    source = Path(source).resolve()
    if not 72 <= dpi <= 600:
        raise ValueError("DPI must be between 72 and 600")
    pdf = pdfium.PdfDocument(str(source))
    try:
        chosen = page_selection(selected, len(pdf))
        dest = fresh_directory(output)
        manifest = {"source_name": source.name, "source_sha256": digest(source),
                    "source_page_count": len(pdf), "dpi": dpi, "pages": []}
        for number in chosen:
            page = pdf[number - 1]
            try:
                image_name = f"page-{number:04d}.png"
                bitmap = page.render(scale=dpi / 72)
                try:
                    pil = bitmap.to_pil()
                    pil.save(dest / image_name)
                    size = list(pil.size)
                    pil.close()
                finally:
                    bitmap.close()
                textpage = page.get_textpage()
                try:
                    text = textpage.get_text_range()
                finally:
                    textpage.close()
                text_name = f"page-{number:04d}.txt"
                (dest / text_name).write_text(text, encoding="utf-8")
                manifest["pages"].append({"source_page": number, "image": image_name,
                                          "image_size": size, "text_layer_file": text_name,
                                          "text_layer_characters": len(text.strip())})
            finally:
                page.close()
        write_json(dest / "manifest.json", manifest)
        return manifest
    finally:
        pdf.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source", type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--pages", help="Only when a subset is requested, e.g. 1,3-5")
    a = p.parse_args()
    result = render(a.source, a.out, a.dpi, a.pages)
    emit({"manifest": str(a.out.resolve() / "manifest.json"), "source_pages": result["source_page_count"],
          "rendered_pages": len(result["pages"])})
