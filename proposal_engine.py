"""
proposal_engine.py
------------------
Data dictionaries + PDF generation (reportlab Platypus).
DOCX generation removed per spec.
"""

import os
import base64
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, Image as RLImage,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────

Deliverables = {
    "website": [
        "UX/UI Design File",
        "Frontend Development",
        "Backend Development",
        "Testing and Deployment",
        "Client Handoff",
        "3 Months of Support",
    ],
    "web application": [
        "UX Research & Analysis",
        "Information Architecture",
        "UX Wireframing",
        "UI Design",
        "Prototyping",
        "Frontend Development",
        "Backend Development",
        "Testing and Deployment",
    ],
    "mobile app": [
        "UX Research & Analysis",
        "Information Architecture",
        "UX Wireframing",
        "UI Design",
        "Prototyping",
        "Frontend Development",
        "Backend Development",
        "Testing and Deployment",
    ],
    "crm": [
        "Idea Generation",
        "Requirement Gathering",
        "System Design",
        "Development",
        "Testing and Deployment",
    ],
}

description = {
    "website":         "Development of a responsive website tailored to the client's brand and goals.",
    "web application": "Development of a full-featured web application for the client.",
    "mobile app":      "Development of a cross-platform mobile application for the client.",
    "crm":             "Development of a custom CRM system to streamline client operations.",
}

pricing = {
    "website":         ("50,000",   "2,00,000"),
    "web application": ("1,00,000", "5,00,000"),
    "mobile app":      ("1,00,000", "5,00,000"),
    "crm":             ("2,00,000", "10,00,000"),
}


# ─────────────────────────────────────────────
# save_pdf — Folio Editor style via reportlab
# ─────────────────────────────────────────────

def save_pdf(client, logo_bytes=None):
    """
    Build a Folio-Editor-style PDF with reportlab Platypus.

    Parameters
    ----------
    client     : dict   Keys: Name, Project Type, Budget, Timeline
    logo_bytes : bytes  Raw image bytes from st.file_uploader, or None

    Returns
    -------
    str  Path to the saved PDF file
    """
    os.makedirs("proposals", exist_ok=True)
    path    = f"proposals/{client['Name']}_proposal.pdf"
    project = client["Project Type"]
    W, H    = A4          # 595 x 842 pt
    M       = 18 * mm     # page margin
    IW      = W - 2 * M   # inner (usable) width

    # ── Colours ─────────────────────────────────
    BLACK = colors.HexColor("#0a0a0a")
    GREY  = colors.HexColor("#999999")
    LGREY = colors.HexColor("#dddddd")
    DARK  = colors.HexColor("#444444")

    # ── Style factory ───────────────────────────
    def S(name, font="Helvetica", size=11, color=BLACK,
          leading=None, sb=0, sa=4, align=TA_LEFT, bold=False):
        return ParagraphStyle(
            name,
            fontName    = font + ("-Bold" if bold else ""),
            fontSize    = size,
            textColor   = color,
            leading     = leading or size * 1.45,
            spaceBefore = sb,
            spaceAfter  = sa,
            alignment   = align,
        )

    # Define all styles
    sPageLabel  = S("pl",   size=8,  color=GREY,  align=TA_RIGHT)
    sTitle      = S("ti",   size=40, bold=True, leading=44, sb=4, sa=14)
    sPrepLabel  = S("prl",  size=8,  color=GREY)
    sClientName = S("cn",   size=22, bold=True, sa=6)
    sDateLabel  = S("dl",   size=8,  color=GREY,  align=TA_RIGHT)
    sDateVal    = S("dv",   size=11, align=TA_RIGHT)
    sSecHead    = S("sh",   size=14, bold=True, sb=8, sa=6)
    sBody       = S("bo",   size=11, color=DARK, leading=17, sa=4)
    sColLabel   = S("cl",   size=8,  color=GREY, sa=5)
    sDeliv      = S("de",   size=11, sa=3)
    sInvLbl     = S("il",   size=8,  color=GREY, sa=2)
    sInvVal     = S("iv",   size=13, bold=True, sa=8)
    sInvBig     = S("ib",   size=18, bold=True, sa=8)
    sSigItalic  = S("si",   size=11, color=colors.HexColor("#555555"), sa=12)
    sSigLabel   = S("sl",   size=8,  color=GREY, sa=2)
    sSigName    = S("sn",   size=12, bold=True)
    sFooter     = S("fl",   size=8,  color=colors.HexColor("#bbbbbb"))
    sFooterR    = S("fr",   size=8,  color=colors.HexColor("#bbbbbb"), align=TA_RIGHT)

    # ── Helper flowables ────────────────────────
    def hr(clr=LGREY, thick=1):
        return HRFlowable(width="100%", thickness=thick,
                          color=clr, spaceBefore=4, spaceAfter=10)

    def section_heading(text):
        """4pt black left-bar accent + bold heading text."""
        BAR_W, GAP_W = 5, 10
        t = Table([["", "", Paragraph(text, sSecHead)]],
                  colWidths=[BAR_W, GAP_W, IW - BAR_W - GAP_W])
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), BLACK),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return t

    # ── Story ───────────────────────────────────
    story = []

    # PAGE LABEL (top-right)
    story.append(Paragraph("PAGE 01 / 04", sPageLabel))
    story.append(Spacer(1, 2))

    # Short decorative black rule (top-left)
    rule = Table([[""]], colWidths=[48], rowHeights=[3])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), BLACK)]))
    story.append(rule)
    story.append(Spacer(1, 16))

    # LOGO (if provided)
    if logo_bytes:
        try:
            img = RLImage(BytesIO(logo_bytes), height=50, width=None)
            img.hAlign = "LEFT"
            story.append(img)
            story.append(Spacer(1, 10))
        except Exception:
            pass   # silently skip broken images

    # GIANT TITLE
    story.append(Paragraph("PROJECT PROPOSAL", sTitle))

    # PREPARED FOR + DATE row
    date_str = datetime.now().strftime("%d %B %Y")
    hdr = Table(
        [
            [Paragraph("PREPARED FOR", sPrepLabel), Paragraph("DATE", sDateLabel)],
            [Paragraph(client["Name"],  sClientName), Paragraph(date_str, sDateVal)],
        ],
        colWidths=[IW * 0.6, IW * 0.4],
    )
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr)
    story.append(hr())

    # OVERVIEW
    story.append(section_heading("Overview"))
    story.append(Paragraph(
        f"We propose a high-quality {project} solution tailored to your "
        f"business objectives and delivered within {client['Timeline']}.",
        sBody,
    ))
    story.append(Spacer(1, 6))
    story.append(hr())

    # SCOPE OF WORK — two columns
    story.append(section_heading("Scope of Work"))
    story.append(Spacer(1, 6))

    delivs = Deliverables.get(project, [])
    left_col = [Paragraph("CORE DELIVERABLES", sColLabel)]
    for d in delivs:
        left_col.append(Paragraph(f"\u2014  {d}", sDeliv))

    mn, mx = pricing.get(project, ("N/A", "N/A"))
    right_col = [
        Paragraph("TIMELINE &amp; INVESTMENT", sColLabel),
        Paragraph("ESTIMATED COMPLETION",      sInvLbl),
        Paragraph(client["Timeline"],          sInvVal),
        Paragraph("TOTAL PROJECT VALUE",       sInvLbl),
        Paragraph(f"Rs. {client['Budget']}",   sInvBig),
        Paragraph("PRICE RANGE",               sInvLbl),
        Paragraph(f"Rs. {mn}  \u2013  Rs. {mx}", sInvVal),
    ]

    # Pad to equal length
    n = max(len(left_col), len(right_col))
    while len(left_col)  < n: left_col.append(Spacer(1, 1))
    while len(right_col) < n: right_col.append(Spacer(1, 1))

    scope = Table(
        [[l, r] for l, r in zip(left_col, right_col)],
        colWidths=[IW * 0.52, IW * 0.48],
    )
    scope.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(scope)
    story.append(Spacer(1, 8))
    story.append(hr())

    # SIGNATURE SECTION
    def sig_col(italic, label, name):
        return [
            Paragraph(f"<i>{italic}</i>", sSigItalic),
            HRFlowable(width="100%", thickness=1, color=BLACK, spaceAfter=6),
            Paragraph(label, sSigLabel),
            Paragraph(name,  sSigName),
        ]

    sl = sig_col("Digital Signature Recorded", "CONSULTANT SIGNATURE",  "Lead Creative Director")
    sr = sig_col("Digital Signature Recorded", "CLIENT AUTHORIZATION",  "Authorized Representative")
    n  = max(len(sl), len(sr))
    while len(sl) < n: sl.append(Spacer(1, 1))
    while len(sr) < n: sr.append(Spacer(1, 1))

    sig = Table([[l, r] for l, r in zip(sl, sr)],
                colWidths=[IW * 0.5, IW * 0.5])
    sig.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    story.append(sig)
    story.append(Spacer(1, 20))

    # FOOTER
    footer = Table(
        [[Paragraph("FOLIO EDITOR \u00a9 2025", sFooter),
          Paragraph("CONFIDENTIAL DOCUMENT",    sFooterR)]],
        colWidths=[IW * 0.5, IW * 0.5],
    )
    footer.setStyle(TableStyle([
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, LGREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(footer)

    # BUILD
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=M,  bottomMargin=M,
    )
    doc.build(story)
    return path
