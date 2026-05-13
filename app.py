"""
app.py  —  POPS Smart Proposal Automation
-----------------------------------------
Streamlit entry point for Streamlit Cloud deployment.

HOW TO RUN LOCALLY:
    streamlit run app.py
"""

import os
import base64
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from proposal_engine import Deliverables, pricing, save_pdf


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  — must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="POPS — Smart Proposal Automation",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Absolute path to the directory containing app.py
# Using this ensures file reads work on Streamlit Cloud too
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebar"] {
    background-color: #1a1f2e !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
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
[data-testid="stSidebar"] label {
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #8892a4 !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background-color: #252b3b !important;
    border: 1px dashed #3a4155 !important;
    border-radius: 6px !important;
}
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
.block-container {
    padding-top: 0 !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}
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
.sidebar-divider {
    border: none;
    border-top: 1px solid #2e3447;
    margin: 16px 0;
}
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
# ─────────────────────────────────────────────────────────────────────────────
for key, default in [
    ("html_filled", None),
    ("pdf_path",    None),
    ("client_name", ""),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(
        "<div style='text-align:center;padding:8px 0 4px;'>"
        "<span style='font-size:22px;font-weight:900;color:#4f46e5;'>"
        "&#9679; POPS</span><br>"
        "<span style='font-size:11px;color:#8892a4;letter-spacing:1px;'>"
        "SMART PROPOSAL AUTOMATION</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    name          = st.text_input("Client Name",  placeholder="e.g. unaku pudicha peru")
    project_type  = st.selectbox("Project Type",  list(Deliverables.keys()), format_func=str.title)
    timeline      = st.text_input("Timeline",     placeholder="e.g. 3 months")
    pricing_input = st.text_input("Pricing (Rs)", placeholder="e.g. 75,000")

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    logo_file = st.file_uploader(
        "Company Logo (optional)",
        type=["png", "jpg", "jpeg"],
        help="Shown at the top of the proposal",
    )

    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

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
    for err in errors:
        st.sidebar.error(err)
    if errors:
        st.stop()

    # Client dictionary
    client = {
        "Name":         name.strip(),
        "Project Type": project_type,
        "Budget":       pricing_input.strip(),
        "Timeline":     timeline.strip(),
    }

    # Deliverables HTML
    items             = Deliverables[project_type]
    deliverables_html = "\n".join(f"<li>{item}</li>" for item in items)

    # Price range
    mn, mx          = pricing.get(project_type, ("N/A", "N/A"))
    price_range_str = f"{mn} \u2013 {mx}"

    # Logo → base64 data-URI (works inside components.html iframe)
    logo_bytes = None
    logo_html  = ""

    if logo_file is not None:
        logo_bytes = logo_file.read()
        ext  = logo_file.name.rsplit(".", 1)[-1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                "png": "image/png"}.get(ext, "image/png")
        b64       = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = (
            f'<div class="logo-row">'
            f'<img src="data:{mime};base64,{b64}" alt="logo">'
            f'</div>'
        )

    # Load HTML template using absolute path
    template_path = os.path.join(BASE_DIR, "Proposal_preview.html")
    with open(template_path, "r", encoding="utf-8") as f:
        tmpl = f.read()

    # Fill all placeholders — must match exactly what the template expects
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

    # Generate PDF with reportlab
    pdf_path = save_pdf(client, logo_bytes=logo_bytes)

    # Persist across reruns
    st.session_state.html_filled = html_filled
    st.session_state.pdf_path    = pdf_path
    st.session_state.client_name = client["Name"]


# ─────────────────────────────────────────────────────────────────────────────
# MAIN AREA
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="navbar">
    <div class="navbar-links">
        <a href="#">Drafts</a>
        <a href="#">Templates</a>
        <a href="#">Archive</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Download PDF button — only shown after generation
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

# Proposal preview
if st.session_state.html_filled:
    components.html(st.session_state.html_filled, height=1150, scrolling=True)
else:
    st.markdown("""
    <div class="empty-hint">
        <span class="big-icon">📄</span>
        <span>Fill in the details on the left and click
              <strong>&#9654; Preview Mode</strong></span>
    </div>
    """, unsafe_allow_html=True)
