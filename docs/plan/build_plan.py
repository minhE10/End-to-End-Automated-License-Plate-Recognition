"""Export the complete Vietnamese plan to a real PDF; no training is performed."""
from __future__ import annotations

import argparse
import hashlib
import html
import os
from pathlib import Path
import re
import sys

PLAN = Path(__file__).resolve().parent
ROOT = PLAN.parents[1]
SOURCES = [PLAN / "README.md"] + [next(PLAN.glob(f"{n:02}-*.md")) for n in range(12)] + [
    PLAN / "decision-log.md", PLAN / "sources-and-reference-review.md"]


def dependencies():
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        raise SystemExit("ReportLab missing. Install requirements-docs.txt; Markdown remains complete.")
    font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
    if not (font_dir / "arial.ttf").is_file() or not (font_dir / "arialbd.ttf").is_file():
        raise SystemExit("Arial Unicode font files missing. Install Arial or adapt font paths; no PDF written.")
    pdfmetrics.registerFont(TTFont("Plan", str(font_dir / "arial.ttf")))
    pdfmetrics.registerFont(TTFont("PlanBold", str(font_dir / "arialbd.ttf")))
    pdfmetrics.registerFontFamily("Plan", normal="Plan", bold="PlanBold", italic="Plan", boldItalic="PlanBold")
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    for path in SOURCES:
        if not path.is_file():
            raise SystemExit(f"Missing Markdown source: {path}")


def inline(text):
    # Keep external URLs visible; local links use labels and remain available in Markdown.
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r"\1 (\2)", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = html.escape(html.unescape(text))
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = text.replace("`", "")
    text = re.sub(r"([\u3400-\u9fff]+)", r'<font name="STSong-Light">\1</font>', text)
    return text


def build(output):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, PageBreak, Table, TableStyle

    styles = {
        "body": ParagraphStyle("body", fontName="Plan", fontSize=9, leading=13, spaceAfter=6,
                               splitLongWords=True, wordWrap="CJK", alignment=TA_LEFT),
        "h1": ParagraphStyle("h1", fontName="PlanBold", fontSize=18, leading=23, spaceAfter=12, keepWithNext=True),
        "h2": ParagraphStyle("h2", fontName="PlanBold", fontSize=13, leading=17, spaceBefore=10, spaceAfter=7, keepWithNext=True),
        "h3": ParagraphStyle("h3", fontName="PlanBold", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=6, keepWithNext=True),
        "cell": ParagraphStyle("cell", fontName="Plan", fontSize=7.7, leading=10.8, wordWrap="CJK", splitLongWords=True),
        "code": ParagraphStyle("code", fontName="Plan", fontSize=7.7, leading=11, wordWrap="CJK", splitLongWords=True,
                               backColor=colors.HexColor("#f0f4f8"), spaceAfter=3),
    }
    story = []
    usable_width = A4[0] - 76

    def paragraph(text, style="body"):
        story.append(Paragraph(inline(text), styles[style]))

    for file_index, path in enumerate(SOURCES):
        if file_index:
            story.append(PageBreak())
        lines = path.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            if line.startswith("```"):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    paragraph(lines[i].replace(" ", "\u00a0"), "code")
                    i += 1
                i += 1
                continue
            if line.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [cell.strip() for cell in lines[i].strip().strip("|").split("|")]
                    if not all(re.fullmatch(r"[:\- ]+", cell) for cell in cells):
                        rows.append(cells)
                    i += 1
                num_cols = max(map(len, rows))
                if any(len(row) != num_cols for row in rows):
                    raise ValueError(f"Malformed Markdown table: {path.name}: {rows}")
                weights = [min(34, max(8, max(len(row[col]) for row in rows) ** 0.68)) for col in range(num_cols)]
                widths = [usable_width * weight / sum(weights) for weight in weights]
                cells = [[Paragraph(inline(cell), styles["cell"]) for cell in row] for row in rows]
                table = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2edf4")),
                    ("GRID", (0, 0), (-1, -1), .35, colors.HexColor("#bcc9d2")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story += [table, Spacer(1, 8)]
                continue
            heading = re.match(r"^(#{1,3})\s+(.+)", line)
            if heading:
                paragraph(heading.group(2), f"h{len(heading.group(1))}")
                i += 1
                continue
            if line.startswith("- "):
                paragraph("• " + line[2:])
                i += 1
                continue
            block = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("#", "|", "```", "- ")):
                block.append(lines[i].strip())
                i += 1
            paragraph(" ".join(block))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Plan", 8)
        canvas.setFillColor(colors.HexColor("#526675"))
        canvas.drawString(38, 23, "ALPR plan-v1 | 08/11/2026 | Kế hoạch, chưa có kết quả mô hình")
        canvas.drawRightString(A4[0] - 38, 23, str(doc.page))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".building.pdf")
    doc = SimpleDocTemplate(str(temporary), pagesize=A4, leftMargin=38, rightMargin=38,
                            topMargin=38, bottomMargin=38, title="ALPR — Kế hoạch triển khai 4 tuần",
                            author="ALPR project planning")
    try:
        doc.build(story, onFirstPage=footer, onLaterPages=footer)
        data = temporary.read_bytes()
        if not data.startswith(b"%PDF-") or len(data) < 1000:
            raise ValueError("PDF export did not produce a valid nonempty document")
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()
    print(f"PDF: {output}\nPages: {doc.page}; bytes: {len(data)}; sha256: {hashlib.sha256(data).hexdigest()}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check tools/fonts/sources without writing a PDF")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/plan/ALPR-Implementation-Plan.pdf")
    args = parser.parse_args()
    dependencies()
    if args.check:
        print(f"PASS: ReportLab, Arial/CJK fonts, {len(SOURCES)} Markdown sources; no PDF written by --check.")
    else:
        build(args.output.resolve())


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as exc:
        print(f"PDF export failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
