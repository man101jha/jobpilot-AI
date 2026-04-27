"""
Modern Resume PDF Generator — uses ReportLab (pure Python, no pdflatex needed).
Parses the AI's Markdown-style output and renders a clean, professional PDF.
Works on every free hosting platform (Render, Railway, Fly.io, etc.)
"""

import re
import io
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

from .resume_template import COLORS, FONT, MARGIN, SPACING


# ---------------------------------------------------------------------------
# Helper — convert (r,g,b) tuple (0-1) to ReportLab Color
# ---------------------------------------------------------------------------
def _c(key):
    r, g, b = COLORS[key]
    return colors.Color(r, g, b)


# ---------------------------------------------------------------------------
# Style factory
# ---------------------------------------------------------------------------
def _build_styles():
    base = dict(fontName="Helvetica", fontSize=FONT["body"],
                leading=FONT["body"] * 1.35, textColor=_c("body"))
    styles = {}

    styles["name"] = ParagraphStyle(
        "name",
        fontName="Helvetica-Bold",
        fontSize=FONT["name"],
        leading=FONT["name"] * 1.2,
        textColor=_c("name"),
        alignment=TA_CENTER,
        spaceAfter=SPACING["after_name"],
    )
    styles["contact"] = ParagraphStyle(
        "contact",
        fontName="Helvetica",
        fontSize=FONT["contact"],
        leading=FONT["contact"] * 1.4,
        textColor=_c("subtitle"),
        alignment=TA_CENTER,
        spaceAfter=SPACING["after_contact"],
    )
    styles["section"] = ParagraphStyle(
        "section",
        fontName="Helvetica-Bold",
        fontSize=FONT["section"],
        leading=FONT["section"] * 1.3,
        textColor=_c("section"),
        spaceBefore=SPACING["before_section"],
        spaceAfter=SPACING["after_section"],
        tracking=1.5,         # letter-spacing for that modern feel
    )
    styles["subheading_title"] = ParagraphStyle(
        "subheading_title",
        fontName="Helvetica-Bold",
        fontSize=FONT["subheading"],
        leading=FONT["subheading"] * 1.3,
        textColor=_c("body"),
    )
    styles["subheading_sub"] = ParagraphStyle(
        "subheading_sub",
        fontName="Helvetica-Oblique",
        fontSize=FONT["date"],
        leading=FONT["date"] * 1.3,
        textColor=_c("subtitle"),
        spaceAfter=SPACING["after_subheading"],
    )
    styles["date"] = ParagraphStyle(
        "date",
        fontName="Helvetica",
        fontSize=FONT["date"],
        leading=FONT["date"] * 1.3,
        textColor=_c("light_gray"),
        alignment=TA_RIGHT,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        **base,
        leftIndent=SPACING["bullet_indent"],
        bulletIndent=0,
        spaceAfter=SPACING["after_bullet"],
        bulletFontName="Helvetica",
        bulletFontSize=9,
        bulletColor=_c("accent"),
    )
    styles["body"] = ParagraphStyle("body", **base, spaceAfter=3)

    return styles


# ---------------------------------------------------------------------------
# Parser — converts the AI's plain-text/Markdown output into structured data
# ---------------------------------------------------------------------------
def _parse_content(raw_text):
    """
    Accepts free-form text (possibly with Markdown headers/bullets) produced
    by the LLM and returns a list of structured blocks.

    Block types:
      {"type": "section",    "text": "EXPERIENCE"}
      {"type": "subheading", "title": "...", "sub": "...", "date": "..."}
      {"type": "bullet",     "text": "..."}
      {"type": "body",       "text": "..."}
    """
    # Strip stale LaTeX artefacts just in case the LLM still leaks them
    raw_text = re.sub(r'\\[a-zA-Z]+(\{[^}]*\})*', ' ', raw_text)
    raw_text = re.sub(r'[{}]', '', raw_text)

    blocks = []
    lines = raw_text.splitlines()
    found_first_heading = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # --- Markdown ATX headings  (## Experience  /  # Education)
        h_match = re.match(r'^#{1,3}\s+(.*)', line)
        if h_match:
            found_first_heading = True
            blocks.append({"type": "section", "text": h_match.group(1).upper()})
            continue

        # --- Markdown setext / ALL-CAPS short lines as section headers
        if re.match(r'^[A-Z][A-Z\s&/]{2,30}$', line):
            found_first_heading = True
            blocks.append({"type": "section", "text": line})
            continue

        # If we haven't found a heading yet, it's likely preamble text to ignore
        if not found_first_heading:
            continue

        # --- Bold title line  **Company | Role | Date**
        bold_match = re.match(r'^\*\*(.+?)\*\*(.*)$', line)
        if bold_match:
            inner = bold_match.group(1).strip()
            rest  = bold_match.group(2).strip().lstrip('–-|').strip()
            # Try to split: Title | Sub | Date
            parts = re.split(r'\s*[|–-]\s*', inner + (" | " + rest if rest else ""))
            parts = [p.strip() for p in parts if p.strip()]
            title = parts[0] if len(parts) > 0 else inner
            sub   = parts[1] if len(parts) > 1 else ""
            date  = parts[2] if len(parts) > 2 else ""
            blocks.append({"type": "subheading", "title": title, "sub": sub, "date": date})
            continue

        # --- Bullet lines  (- • * ›)
        bullet_match = re.match(r'^[-•*›]\s+(.*)', line)
        if bullet_match:
            blocks.append({"type": "bullet", "text": bullet_match.group(1)})
            continue

        # --- Numbered list
        num_match = re.match(r'^\d+\.\s+(.*)', line)
        if num_match:
            blocks.append({"type": "bullet", "text": num_match.group(1)})
            continue

        # --- Plain body text
        blocks.append({"type": "body", "text": line})

    return blocks


# ---------------------------------------------------------------------------
# Main PDF generator
# ---------------------------------------------------------------------------
def generate_resume_pdf(data_dict, output_path="updated_resume"):
    """
    Build a modern resume PDF from a data dictionary.

    data_dict keys:
        name         – candidate full name
        contact_info – email | phone | location (pipe-separated)
        content      – the AI-generated resume body (Markdown / plain text)

    Returns the output .pdf filename or None on error.
    """
    try:
        pdf_file = f"{output_path}.pdf"
        styles = _build_styles()

        # Page setup
        doc = SimpleDocTemplate(
            pdf_file,
            pagesize=LETTER,
            leftMargin=MARGIN["left"],
            rightMargin=MARGIN["right"],
            topMargin=MARGIN["top"],
            bottomMargin=MARGIN["bottom"],
        )

        story = []

        # ---- Header -------------------------------------------------------
        name = data_dict.get("name", "Resume")
        story.append(Paragraph(name.upper(), styles["name"]))

        contact_raw = data_dict.get("contact_info", "")
        # Replace pipe with a nice separator
        contact_html = contact_raw.replace("|", " &nbsp;·&nbsp; ")
        story.append(Paragraph(contact_html, styles["contact"]))

        # Full-width accent rule under header
        story.append(HRFlowable(
            width="100%",
            thickness=2.5,
            color=_c("accent"),
            spaceAfter=8,
        ))

        # ---- Body ---------------------------------------------------------
        raw_content = data_dict.get("content", "")
        blocks = _parse_content(raw_content)

        usable_w = LETTER[0] - MARGIN["left"] - MARGIN["right"]

        for block in blocks:
            btype = block["type"]

            if btype == "section":
                story.append(Spacer(1, SPACING["before_section"]))
                story.append(Paragraph(block["text"], styles["section"]))
                story.append(HRFlowable(
                    width="100%",
                    thickness=SPACING["section_rule_width"],
                    color=_c("rule"),
                    spaceAfter=SPACING["after_section"],
                ))

            elif btype == "subheading":
                title_p = Paragraph(block["title"], styles["subheading_title"])
                date_p  = Paragraph(block["date"],  styles["date"])
                sub_p   = Paragraph(block["sub"],   styles["subheading_sub"])

                # Two-column table: [Title ... Date]
                heading_table = Table(
                    [[title_p, date_p]],
                    colWidths=[usable_w * 0.72, usable_w * 0.28],
                )
                heading_table.setStyle(TableStyle([
                    ("VALIGN",  (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING",   (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING",(0, 0), (-1, -1), 2),
                ]))

                group = [heading_table]
                if block.get("sub"):
                    group.append(sub_p)
                story.append(KeepTogether(group))

            elif btype == "bullet":
                story.append(Paragraph(f"• &nbsp;{block['text']}", styles["bullet"]))

            else:  # body
                story.append(Paragraph(block["text"], styles["body"]))

        # ---- Build PDF ----------------------------------------------------
        doc.build(story)
        return pdf_file

    except Exception as e:
        print(f"PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return None
