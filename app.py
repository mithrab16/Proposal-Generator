"""
app.py  —  Folio Editor
-----------------------
Streamlit UI: dark navy sidebar + white paper preview panel.

HOW TO RUN:
    streamlit run app.py
"""

import os
import base64
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from proposal_engine import Deliverables, pricing, save_pdf


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be the very first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Folio Editor",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Sidebar ──────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #1a1f2e !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Input fields inside sidebar */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    background-color: #252b3b !important;
    border: 1px solid #3a4155 !important;
    color: #ffffff !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] {
    background-color: #252b3b !important;
    border: 1px solid #3a4155 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
    background-color: #252b3b !important;
    color: #ffffff !important;
}

/* Labels */
[data-testid="stSidebar"] label {
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #8892a4 !important;
    font-weight: 600 !important;
}

/* File uploader area */
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color: #252b3b !important;
    border: 1px dashed #3a4155 !important;
    border-radius: 6px !important;
}

/* Orange Preview Mode button */
[data-testid="stSidebar"] .stButton > button {
    background-color: #ff6b2b !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 12px 0 !important;
    width: 100% !important;
    font-size: 13px !important;
    margin-top: 8px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #e55a1f !important;
}

/* ── Main area ────────────────────────────────────── */
.block-container {
    padding-top: 0 !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Navbar */
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 0;
    border-bottom: 1px solid #e8e8e8;
    margin-bottom: 24px;
}
.navbar-links { display: flex; gap: 28px; }
.navbar-links a {
    font-size: 13px;
    font-weight: 600;
    color: #555;
    text-decoration: none;
    letter-spacing: 0.5px;
}
.navbar-links a:hover { color: #111; }

/* Nav items in sidebar */
.nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    margin-bottom: 4px;
    font-size: 13px;
    font-weight: 500;
    color: #8892a4;
}
.nav-item.active { background: #252b3b; color: #ffffff; }
.nav-icon { font-size: 15px; }

/* Sidebar divider */
.sidebar-divider {
    border: none;
    border-top: 1px solid #2e3447;
    margin: 16px 0;
}

/* Empty state */
.empty-hint {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 520px;
    color: #bbb;
    font-size: 14px;
    gap: 14px;
    border: 2px dashed #e0e0e0;
    border-radius: 12px;
    margin-top: 8px;
}
.empty-hint .big-icon { font-size: 52px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# WHY: Streamlit reruns the whole script on every interaction.
#      session_state keeps the generated preview + PDF alive between reruns.
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("html_filled",  None),
    ("pdf_path",     None),
    ("client_name",  ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    # App name
    st.markdown("## 📄 Folio Editor")
    st.markdown(
        "<p style='font-size:12px;color:#8892a4;margin-top:-8px;'>"
        "Professional Proposal Builder</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # ── Inputs ────────────────────────────────────
    name              = st.text_input("Client Name",  placeholder="e.g. unaku pudicha name")
    project_type      = st.selectbox("Project Type",  ["website", "web application", "mobile app", "crm"])
    timeline          = st.text_input("Timeline",     placeholder="e.g. 3 months")
    pricing_input     = st.text_input("Pricing (₹)",  placeholder="e.g. 75,000")
    deliverables_custom = st.text_area(
        "Custom Deliverables (optional)",
        placeholder="One item per line\nLeave blank to use defaults",
        height=100,
    )

    # ── Logo upload ───────────────────────────────
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    logo_file = st.file_uploader(
        "Company Logo (optional)",
        type=["png", "jpg", "jpeg", "svg"],
        help="Appears in the proposal header at 80px height",
    )

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # ── Nav items ─────────────────────────────────
    st.markdown("""
    <div class="nav-item active">
        <span class="nav-icon">👤</span> Client Details
    </div>
    <div class="nav-item">
        <span class="nav-icon">📋</span> Project Scope
    </div>
    <div class="nav-item">
        <span class="nav-icon">💰</span> Pricing
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # ── Generate button ───────────────────────────
    generate = st.button("▶  Preview Mode", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# GENERATE LOGIC
# ─────────────────────────────────────────────────────────────────────────────
if generate:

    # Validation
    errors = []
    if not name.strip():          errors.append("Client Name is required.")
    if not timeline.strip():      errors.append("Timeline is required.")
    if not pricing_input.strip(): errors.append("Pricing is required.")
    for e in errors:
        st.sidebar.error(e)
    if errors:
        st.stop()

    # Client dict
    client = {
        "Name":         name.strip(),
        "Project Type": project_type,
        "Budget":       pricing_input.strip(),
        "Timeline":     timeline.strip(),
    }

    # Deliverables list
    if deliverables_custom.strip():
        items = [l.strip() for l in deliverables_custom.splitlines() if l.strip()]
    else:
        items = Deliverables[project_type]

    deliverables_html = "\n".join(f"<li>{item}</li>" for item in items)

    # Price range
    mn, mx = pricing.get(project_type, ("N/A", "N/A"))
    price_range_str = f"{mn} \u2013 {mx}"

    # ── Logo handling ──────────────────────────────
    # WHY base64?
    #   The HTML preview runs inside an iframe (components.html).
    #   External file paths don't work there. Embedding the image
    #   as a base64 data-URI makes it self-contained — works in
    #   both the browser iframe AND the reportlab PDF.
    logo_bytes = None
    logo_html  = ""          # empty string → placeholder renders nothing

    if logo_file is not None:
        logo_bytes = logo_file.read()
        # Detect MIME type from file extension
        ext  = logo_file.name.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png",  "svg": "image/svg+xml"}.get(ext, "image/png")
        b64  = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = (
            f'<div class="logo-row">'
            f'<img src="data:{mime};base64,{b64}" alt="logo">'
            f'</div>'
        )

    # ── Fill HTML template ─────────────────────────
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "Proposal_preview.html")
    with open(template_path, "r", encoding="utf-8") as f:
        tmpl = f.read()

    html_filled = tmpl.format(
        logo_html    = logo_html,
        name         = client["Name"],
        project_type = client["Project Type"].title(),
        date         = datetime.now().strftime("%d %B %Y"),
        overview     = (
            f"We propose a high-quality {client['Project Type']} solution "
            f"tailored to your business objectives and delivered within "
            f"{client['Timeline']}."
        ),
        timeline     = client["Timeline"],
        budget       = client["Budget"],
        deliverables = deliverables_html,
        price_range  = price_range_str,
    )

    # ── Generate PDF ───────────────────────────────
    # save_pdf() uses reportlab — no external dependencies needed.
    # logo_bytes is passed separately so reportlab can embed the image
    # directly (base64 strings don't work in reportlab Image).
    pdf_path = save_pdf(client, logo_bytes=logo_bytes)

    # Persist to session state
    st.session_state.html_filled = html_filled
    st.session_state.pdf_path    = pdf_path
    st.session_state.client_name = client["Name"]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA — navbar + preview
# ─────────────────────────────────────────────────────────────────────────────

# Navbar
st.markdown("""
<div class="navbar">
    <div class="navbar-links">
        <a href="#">Drafts</a>
        <a href="#">Templates</a>
        <a href="#">Archive</a>
    </div>
</div>
""", unsafe_allow_html=True)

# PDF download button (top-right, only when a PDF exists)
if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
    _, btn_col = st.columns([6, 1])
    with btn_col:
        with open(st.session_state.pdf_path, "rb") as f:
            st.download_button(
                label     = "⬇ Download PDF",
                data      = f.read(),
                file_name = f"{st.session_state.client_name}_proposal.pdf",
                mime      = "application/pdf",
                use_container_width=True,
            )

# Preview panel
if st.session_state.html_filled:
    components.html(st.session_state.html_filled, height=1150, scrolling=True)
else:
    st.markdown("""
    <div class="empty-hint">
        <span class="big-icon">📄</span>
        <span>Fill in the details on the left and click <strong>▶ Preview Mode</strong></span>
    </div>
    """, unsafe_allow_html=True)
