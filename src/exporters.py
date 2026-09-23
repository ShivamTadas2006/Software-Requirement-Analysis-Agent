"""
Exporters module for saving SRS documents in TXT, Markdown, and PDF formats.
"""
import os
import re
from typing import Dict, Any
from fpdf import FPDF


def sanitize_text_for_pdf(text: str) -> str:
    """
    Replaces unicode quotes, dashes, and special characters with standard equivalents
    to ensure safe PDF rendering across all platforms.
    """
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2026": "...",
        "\u2022": "*",
        "\u2192": "->",
        "\u2264": "<=",
        "\u2265": ">=",
        "🟢": "[Acceptable]",
        "🟡": "[Needs Improvement]",
        "🔴": "[Critical Issues]",
        "⚪": "[Notice]",
        "🚀": "",
        "🔒": "",
        "⚠️": "",
        "⚡": "",
        "🎯": "",
        "📋": "",
        "⚙️": "",
        "🛡️": "",
        "👥": "",
        "🔍": "",
        "✨": "",
        "📄": "",
        "📝": ""
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Remove any remaining unprintable or surrogate characters
    return text.encode("latin-1", "replace").decode("latin-1")


class SRS_PDF(FPDF):
    """Custom FPDF subclass with professional header, footer, and styling."""

    def __init__(self, title_text="SOFTWARE REQUIREMENTS SPECIFICATION"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_title = title_text
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, sanitize_text_for_pdf(self.doc_title), border=0, align="L")
            self.cell(0, 8, "IEEE 830 / ISO 29148 Standard", border=0, align="R", new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(220, 220, 220)
            self.line(10, 18, 200, 18)
            self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f"Page {self.page_no()} of {{nb}}", align="C")


def export_to_markdown(srs_markdown: str, output_path: str) -> str:
    """Exports the SRS document as a standard Markdown file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srs_markdown)
    return output_path


def export_to_txt(srs_markdown: str, output_path: str) -> str:
    """Exports the SRS document as a clean, formatted plain text file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Strip markdown bold, italics, backticks
    text = srs_markdown
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"> \*\"([^\"]+)\"\*", r'  "\1"', text)
    text = re.sub(r"> ", "  ", text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path


def export_to_pdf(srs_markdown: str, analysis_data: Dict[str, Any], output_path: str) -> str:
    """
    Exports the SRS document to a styled PDF using fpdf2.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sys_name = analysis_data.get("system_overview", {}).get("system_name", "Software System")
    pdf = SRS_PDF(title_text=f"SRS - {sys_name}")
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title Banner
    pdf.set_fill_color(33, 53, 85)  # Navy Blue
    pdf.rect(10, 15, 190, 32, "F")

    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_xy(15, 20)
    pdf.cell(180, 8, "SOFTWARE REQUIREMENTS SPECIFICATION (SRS)", align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 12)
    pdf.set_xy(15, 29)
    pdf.cell(180, 7, sanitize_text_for_pdf(f"Project: {sys_name}"), align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_xy(15, 37)
    pdf.cell(180, 6, "Compliant with IEEE Std 830-1998 / ISO/IEC/IEEE 29148:2018", align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(52)
    pdf.set_text_color(40, 40, 40)

    # Process markdown lines
    lines = srs_markdown.split("\n")
    in_code_block = False

    for line in lines:
        raw_line = line.strip()

        # Handle code blocks
        if raw_line.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 8)
            pdf.set_text_color(70, 70, 70)
            pdf.cell(0, 4, sanitize_text_for_pdf(line), new_x="LMARGIN", new_y="NEXT")
            continue

        # Skip main title since we drew banner
        if raw_line.startswith("# ") or raw_line.startswith("## Project Title:"):
            continue

        # Section Headings (### 1. Introduction, etc.)
        if raw_line.startswith("### "):
            pdf.ln(4)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(33, 53, 85)
            heading_text = raw_line.replace("### ", "")
            pdf.cell(0, 7, sanitize_text_for_pdf(heading_text), new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(33, 53, 85)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)
            pdf.set_text_color(40, 40, 40)
            continue

        # Sub-headings (#### Feature Title)
        if raw_line.startswith("#### "):
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(50, 60, 80)
            heading_text = raw_line.replace("#### ", "")
            pdf.cell(0, 6, sanitize_text_for_pdf(heading_text), new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(40, 40, 40)
            continue

        # Section separator
        if raw_line.startswith("---"):
            pdf.set_draw_color(220, 220, 220)
            pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
            pdf.ln(3)
            continue

        # Table rows (| Col 1 | Col 2 | ...)
        if raw_line.startswith("|") and raw_line.endswith("|"):
            # Check if separator row (|:---|:---|)
            if re.match(r"^\|[\s:\-]+\|", raw_line):
                continue
            cells = [c.strip() for c in raw_line.split("|")[1:-1]]
            if not cells or all(c == "" for c in cells):
                continue

            # Format table row
            is_header = any(keyword in cells[0].lower() for keyword in ["id", "term", "user class", "entity name", "risk", "original", "quality"])
            if is_header:
                pdf.set_font("Helvetica", "B", 8)
                pdf.set_fill_color(235, 240, 245)
                pdf.set_text_color(33, 53, 85)
            else:
                pdf.set_font("Helvetica", "", 8)
                pdf.set_fill_color(252, 252, 252)
                pdf.set_text_color(50, 50, 50)

            row_str = " | ".join(cells)
            clean_row = sanitize_text_for_pdf(row_str)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 5, clean_row, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
            continue

        # Bullet lists
        if raw_line.startswith("- ") or raw_line.startswith("* "):
            pdf.set_font("Helvetica", "", 9)
            bullet_text = raw_line[2:].replace("**", "").replace("`", "")
            pdf.set_x(14)
            pdf.multi_cell(pdf.epw - 4, 5, f"- {sanitize_text_for_pdf(bullet_text)}", new_x="LMARGIN", new_y="NEXT")
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", raw_line):
            pdf.set_font("Helvetica", "", 9)
            clean_num = re.sub(r"^\d+\.\s*", "", raw_line).replace("**", "").replace("`", "")
            pdf.set_x(16)
            pdf.multi_cell(pdf.epw - 6, 5, f"* {sanitize_text_for_pdf(clean_num)}", new_x="LMARGIN", new_y="NEXT")
            continue

        # Blockquote (> text)
        if raw_line.startswith(">"):
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(80, 80, 80)
            quote_text = raw_line.replace("> ", "").replace("*", "").replace('"', "")
            pdf.set_x(14)
            pdf.multi_cell(pdf.epw - 4, 5, f'"{sanitize_text_for_pdf(quote_text)}"', new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(40, 40, 40)
            continue

        # Regular paragraph
        if raw_line:
            pdf.set_font("Helvetica", "", 9)
            clean_para = raw_line.replace("**", "").replace("`", "").replace("*", "")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(pdf.epw, 5, sanitize_text_for_pdf(clean_para), new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.ln(2)

    pdf.output(output_path)
    return output_path
