"""
proposal_engine.py  —  POPS / Folio Editor
-------------------------------------------
Data dictionaries + PDF generation.

PDF library: reportlab (pure-Python, no system dependencies).
Works on Streamlit Cloud, Windows, Linux, macOS without any
extra system packages.

NOTE: xhtml2pdf was evaluated but its python-bidi dependency
requires a Rust compiler to build on Python 3.12, which is not
available on Streamlit Cloud. reportlab is used instead.
"""

import os
from io import BytesIO
from datetime import datetime

# ── reportlab — the only PDF library used ────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    Image as RLImage,
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────

Deliverables = {
    "website": [
        "Discovery & Strategy",
        "UX Research",
        "UI Design System",
        "Responsive Frontend Development",
        "Backend Integration",
        "QA Testing",
        "Deployment",
        "Post-launch Support",
    ],
    "web application": [
        "Product Architecture",
        "Dashboard Design",
        "Authentication System",
        "API Development",
        "Database Integration",
        "Testing",
        "Deployment",
    ],
    "mobile app": [
        "App Flow Mapping",
        "UI/UX Design",
        "Native Development",
        "API Integration",
        "Performance Optimization",
        "App Deployment",
    ],
    "crm": [
        "Workflow Planning",
        "Database Structure",
        "Admin Dashboard",
        "User Roles & Permissions",
        "Automation Logic",
        "Reporting System",
        "Deployment",
    ],
}

pricing = {
    "website":         ("50,000",   "2,00,000"),
    "web application": ("1,00,000", "5,00,000"),
    "mobile app":      ("1,00,000", "5,00,000"),
    "crm":             ("2,00,000", "10,00,000"),
}

description = {
    "website":         "a responsive, high-performance website",
    "web application": "a full-featured, scalable web application",
    "mobile app":      "a cross-platform mobile application",
    "crm":             "a custom CRM system",
}

CLOSING_NOTE = (
    "Thank you for considering us as your digital transformation partner. "
    "We are committed to delivering scalable, impactful solutions designed "
    "for long-term growth."
)


# ─────────────────────────────────────────────────────────────────────────────
# save_pdf
# ─────────────────────────────────────────────────────────────────────────────

def save_pdf(client, logo_bytes=None):
    """
    Generate a professional proposal PDF with reportlab Platypus.

    Parameters
    ----------
    client     : dict   Keys: Name, Project Type, Budget, Timeline
    logo_bytes : bytes  Raw image bytes from st.file_uploader, or None

    Returns
    -------
    str  Absolute path to the saved PDF file
    """
    os.makedirs("proposals", exist_ok=True)

    client_name  = client.get("Name", "proposal")
    project_type = client.get("Project Type", "website")
    timeline     = client.get("Timeline", "")
    budget       = client.get("Budget", "")

    # Use absolute path so it works regardless of working directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(base_dir, "proposals", f"{client_name}_proposal.pdf")
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    W, H = A4           # 595 × 842 pt
    M    = 20 * mm      # page margin
    IW   = W - 2 * M    # inner width ≈ 515 pt

    # ── Colours ──────────────────────────────────
    BLACK    = colors.HexColor("#0d0d0d")
    ACCENT   = colors.HexColor("#4f46e5")
    GREY     = colors.HexColor("#888888")
    LGREY    = colors.HexColor("#e0e0e0")
    DARK     = colors.HexColor("#333333")
    PRICE_BG = colors.HexColor("#f5f3ff")

    # ── Style factory ─────────────────────────────
    def S(name, font="Helvetica", size=11, color=BLACK,
          leading=None, sb=0, sa=4, align=TA_LEFT, bold=False):
        return ParagraphStyle(
            name,
            fontName    = font + ("-Bold" if bold else ""),
            fontSize    = size,
            textColor   = color,
            leading     = leading or size * 1.5,
            spaceBefore = sb,
            spaceAfter  = sa,
            alignment   = align,
        )

    sBrandName  = S("bn",  size=24, color=ACCENT, bold=True,  align=TA_LEFT, sa=2)
    sBrandSub   = S("bs",  size=9,  color=GREY,   align=TA_LEFT, sa=0)
    sDate       = S("dt",  size=10, color=GREY,   align=TA_RIGHT)
    sTitle      = S("ti",  size=36, bold=True, leading=40, sb=6, sa=12)
    sSecHead    = S("sh",  size=13, bold=True, color=BLACK, sb=8, sa=5)
    sBody       = S("bo",  size=11, color=DARK, leading=17, sa=4)
    sColLabel   = S("cl",  size=8,  color=GREY, sa=5)
    sDeliv      = S("de",  size=11, color=DARK, sa=3)
    sInvLabel   = S("il",  size=8,  color=GREY, sa=2)
    sInvVal     = S("iv",  size=13, bold=True, sa=6)
    sInvRange   = S("ir",  size=16, bold=True, color=ACCENT, sa=0)
    sSigItalic  = S("si",  size=10, color=GREY, sa=10)
    sSigLabel   = S("sl",  size=8,  color=GREY, sa=2)
    sSigName    = S("sn",  size=11, bold=True)
    sFooterL    = S("fl",  size=8,  color=GREY)
    sFooterR    = S("fr",  size=8,  color=GREY, align=TA_RIGHT)
    sClosing    = S("cn",  size=11, color=DARK, leading=17, sa=4)

    # ── Helpers ───────────────────────────────────
    def hr(clr=LGREY, thick=0.75, sb=4, sa=10):
        return HRFlowable(
            width="100%", thickness=thick,
            color=clr, spaceBefore=sb, spaceAfter=sa,
        )

    def section_heading(text):
        """Indigo 4pt left-bar + bold heading."""
        BAR_W, GAP_W = 4, 10
        t = Table(
            [["", "", Paragraph(text, sSecHead)]],
            colWidths=[BAR_W, GAP_W, IW - BAR_W - GAP_W],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (0, 0), ACCENT),
            ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        return t

    # ── Story ─────────────────────────────────────
    story = []
    date_str = datetime.now().strftime("%d %B %Y")

    # BRAND HEADER
    if logo_bytes:
        try:
            img = RLImage(BytesIO(logo_bytes), height=44, width=None)
            img.hAlign = "LEFT"
            story.append(img)
            story.append(Spacer(1, 6))
        except Exception:
            pass  # skip broken images silently

    story.append(Paragraph("\u25cf POPS", sBrandName))
    story.append(Paragraph("Smart Proposal Automation", sBrandSub))
    story.append(Spacer(1, 14))
    story.append(hr(clr=ACCENT, thick=1.5, sb=0, sa=14))

    # DATE
    story.append(Paragraph(date_str, sDate))
    story.append(Spacer(1, 8))

    # TITLE
    story.append(Paragraph("PROJECT PROPOSAL", sTitle))
    story.append(hr())

    # OVERVIEW
    story.append(section_heading("Overview"))
    desc = description.get(project_type, "a tailored digital solution")
    story.append(Paragraph(
        f"We are pleased to present this proposal for {desc}. "
        f"Our team will deliver a scalable, high-quality product within "
        f"{timeline}, aligned with your business objectives.",
        sBody,
    ))
    story.append(Spacer(1, 6))
    story.append(hr())

    # SCOPE OF WORK
    story.append(section_heading("Scope of Work"))
    story.append(Spacer(1, 6))

    delivs = Deliverables.get(project_type, [])
    left_col = [Paragraph("CORE DELIVERABLES", sColLabel)]
    for d in delivs:
        left_col.append(Paragraph(f"\u2014\u2002{d}", sDeliv))

    mn, mx = pricing.get(project_type, ("N/A", "N/A"))
    right_col = [
        Paragraph("TIMELINE &amp; INVESTMENT", sColLabel),
        Paragraph("ESTIMATED COMPLETION",      sInvLabel),
        Paragraph(timeline,                    sInvVal),
        Spacer(1, 6),
        Paragraph("INVESTMENT RANGE",          sInvLabel),
    ]

    # Pricing box
    price_box = Table(
        [[Paragraph(f"Rs. {mn} \u2013 Rs. {mx}", sInvRange)]],
        colWidths=[IW * 0.46 - 16],
    )
    price_box.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), PRICE_BG),
        ("TOPPADDING",    (0, 0), (0, 0), 10),
        ("BOTTOMPADDING", (0, 0), (0, 0), 10),
        ("LEFTPADDING",   (0, 0), (0, 0), 12),
        ("RIGHTPADDING",  (0, 0), (0, 0), 12),
    ]))
    right_col.append(price_box)

    # Pad columns to equal length
    n = max(len(left_col), len(right_col))
    while len(left_col)  < n: left_col.append(Spacer(1, 1))
    while len(right_col) < n: right_col.append(Spacer(1, 1))

    scope = Table(
        [[l, r] for l, r in zip(left_col, right_col)],
        colWidths=[IW * 0.54, IW * 0.46],
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

    # CLOSING NOTE
    story.append(section_heading("Closing Note"))
    story.append(Paragraph(CLOSING_NOTE, sClosing))
    story.append(Spacer(1, 16))
    story.append(hr())

    # SIGNATURE SECTION
    def sig_col(label, name):
        return [
            Paragraph("<i>Digital Signature Recorded</i>", sSigItalic),
            HRFlowable(width="100%", thickness=0.75, color=BLACK, spaceAfter=5),
            Paragraph(label, sSigLabel),
            Paragraph(name,  sSigName),
        ]

    sl = sig_col("CONSULTANT SIGNATURE", "Lead Creative Director")
    sr = sig_col("CLIENT AUTHORIZATION", "Authorized Representative")
    n  = max(len(sl), len(sr))
    while len(sl) < n: sl.append(Spacer(1, 1))
    while len(sr) < n: sr.append(Spacer(1, 1))

    sig = Table(
        [[l, r] for l, r in zip(sl, sr)],
        colWidths=[IW * 0.5, IW * 0.5],
    )
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
        [[Paragraph("POPS \u00a9 2025  \u2022  Smart Proposal Automation", sFooterL),
          Paragraph("CONFIDENTIAL DOCUMENT", sFooterR)]],
        colWidths=[IW * 0.6, IW * 0.4],
    )
    footer.setStyle(TableStyle([
        ("LINEABOVE",     (0, 0), (-1, 0), 0.5, LGREY),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
    ]))
    story.append(footer)

    # BUILD PDF
    doc = SimpleDocTemplate(
        pdf_path, pagesize=A4,
        leftMargin=M, rightMargin=M,
        topMargin=M,  bottomMargin=M,
    )
    doc.build(story)
    return pdf_path
