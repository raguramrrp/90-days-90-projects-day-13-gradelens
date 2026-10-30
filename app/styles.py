"""
GradeLens Professional Commercial Design System.
Strictly adheres to the specified clean, high-contrast light academic analytics theme:
Main background: #F5F8FC, Surface: #FFFFFF, Primary Text: #102B50, Primary Blue: #2878E5,
Borders: #E2EAF3, Success: #16A58A, Warning: #E6A52E, Critical: #E35D63.
"""

THEME_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

    /* Global Typography - NEVER force !important on span/div to protect icon fonts */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #102B50;
        background-color: #F5F8FC !important;
    }
    p, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Streamlit Material Icons Fix: preserve Google Material Symbols ligatures */
    span[data-testid="stIconMaterial"],
    [class*="material-symbols"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stExpandSidebarButton"] span {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 1.25rem !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }

    /* Main Content Container Spacing: Ensure clean clearance below header */
    .block-container {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 1360px !important;
    }

    /* Header & Top Bar: Hide Streamlit branding & Deploy button, keep sidebar expand toggle */
    header[data-testid="stHeader"] {
        background: transparent !important;
        height: 2.5rem !important;
        z-index: 99 !important;
    }
    .stDeployButton,
    [data-testid="stAppDeployButton"],
    [data-testid="stHeaderActionElements"],
    [data-testid="stToolbar"],
    [data-testid="stToolbarActions"],
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    header [data-testid="manage-app-button"],
    header button[title*="Deploy" i],
    header button[aria-label*="Deploy" i],
    header button:not([data-testid="stSidebarCollapseButton"]):not([data-testid="stExpandSidebarButton"]),
    #MainMenu,
    footer {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Expand Sidebar Toggle (only when sidebar is collapsed) */
    section[data-testid="stSidebar"]:not([aria-expanded="false"]) ~ * [data-testid="stExpandSidebarButton"],
    .stApp:has(section[data-testid="stSidebar"]:not([aria-expanded="false"])) [data-testid="stExpandSidebarButton"] {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="stExpandSidebarButton"] {
        align-items: center !important;
        justify-content: center !important;
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 4px !important;
        box-shadow: 0 1px 3px rgba(16, 43, 80, 0.12) !important;
        color: #102B50 !important;
        cursor: pointer !important;
        padding: 4px 6px !important;
        margin-left: 0.6rem !important;
        margin-top: 0.35rem !important;
    }
    [data-testid="stExpandSidebarButton"]:hover {
        background-color: #EAF3FF !important;
        border-color: #2878E5 !important;
        color: #2878E5 !important;
    }

    /* Sidebar Container Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2EAF3 !important;
        box-shadow: none !important;
        min-width: 255px !important;
    }

    /* Sidebar Scrollbar Styling */
    section[data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 4px !important;
    }
    section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background-color: #E2EAF3 !important;
        border-radius: 4px !important;
    }

    /* Sidebar Header & Collapse Toggle */
    [data-testid="stSidebarHeader"] {
        padding: 0.4rem 0.6rem 0.2rem 0.6rem !important;
        background-color: #FFFFFF !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        color: #102B50 !important;
        background-color: #F5F8FC !important;
        border: 1px solid #E2EAF3 !important;
        border-radius: 4px !important;
        padding: 3px !important;
    }
    [data-testid="stSidebarCollapseButton"]:hover {
        background-color: #EAF3FF !important;
        color: #2878E5 !important;
        border-color: #2878E5 !important;
    }

    /* Sidebar Selectbox Label Styling (compact, zero overlap) */
    section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"],
    section[data-testid="stSidebar"] label {
        font-size: 0.68rem !important;
        font-weight: 700 !important;
        color: #8F9CAE !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
        margin-bottom: 2px !important;
        line-height: 1.1 !important;
        display: block !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] {
        border-radius: 4px !important;
        border-color: #E2EAF3 !important;
        min-height: 34px !important;
    }

    /* Sidebar Navigation Section Titles (st.caption based - zero overlap) */
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] {
        margin-top: 10px !important;
        margin-bottom: 2px !important;
        padding-left: 4px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p {
        font-size: 0.66rem !important;
        font-weight: 700 !important;
        color: #8F9CAE !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        line-height: 1.3 !important;
    }

    /* Sidebar Navigation Buttons - Sleek, Left-Aligned SaaS Navigation */
    section[data-testid="stSidebar"] div[data-testid="stButton"] {
        width: 100% !important;
        margin-bottom: 1px !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center !important;
        text-align: left !important;
        font-size: 0.83rem !important;
        font-weight: 500 !important;
        padding: 0.35rem 0.75rem !important;
        min-height: 32px !important;
        border-radius: 4px !important;
        transition: all 0.15s ease-in-out !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button div[data-testid="stMarkdownContainer"] {
        width: 100% !important;
        text-align: left !important;
        display: flex !important;
        justify-content: flex-start !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button p {
        text-align: left !important;
        width: 100% !important;
        margin: 0 !important;
        line-height: 1.25 !important;
    }

    /* Active Sidebar Navigation Button (Primary) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #EAF3FF !important;
        color: #2878E5 !important;
        border: 1px solid #BFDCFF !important;
        border-left: 3px solid #2878E5 !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #DDEBFF !important;
        color: #1E66C7 !important;
        border-color: #2878E5 !important;
    }

    /* Inactive Sidebar Navigation Button (Secondary) */
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #102B50 !important;
        border: 1px solid transparent !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background-color: #F5F8FC !important;
        color: #2878E5 !important;
        border-color: #E2EAF3 !important;
    }

    /* Main Area Button Styling */
    .stButton > button {
        border-radius: 4px !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        padding: 0.35rem 0.9rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #2878E5 !important;
        border: 1px solid #2878E5 !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #1E66C7 !important;
        border-color: #1E66C7 !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2EAF3 !important;
        color: #102B50 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        border-color: #CBD5E1 !important;
        background-color: #F8FAFC !important;
    }

    /* Professional Headings */
    h1, h2, h3, h4 {
        color: #102B50 !important;
        font-weight: 700 !important;
        letter-spacing: -0.015em !important;
    }
    h1 { font-size: 1.65rem !important; margin-bottom: 0.2rem !important; }
    h2 { font-size: 1.25rem !important; margin-top: 1.2rem !important; margin-bottom: 0.4rem !important; }
    h3 { font-size: 1.05rem !important; }

    /* Surface Card */
    .gl-card {
        background-color: #FFFFFF;
        border: 1px solid #E2EAF3;
        border-radius: 6px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(16, 43, 80, 0.04);
    }

    /* KPI Metric Card */
    .gl-kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2EAF3;
        border-radius: 6px;
        padding: 16px 18px;
        box-shadow: 0 1px 2px rgba(16, 43, 80, 0.03);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .gl-kpi-label {
        font-size: 0.76rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 6px;
    }
    .gl-kpi-value {
        font-size: 1.95rem;
        font-weight: 700;
        color: #102B50;
        line-height: 1.15;
    }
    .gl-kpi-sub {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Section Subheadings */
    .gl-section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #102B50;
        margin-top: 18px;
        margin-bottom: 10px;
        padding-bottom: 6px;
        border-bottom: 1px solid #E2EAF3;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* Status Badges */
    .badge-pill {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        border-radius: 4px;
        letter-spacing: 0.02em;
    }
    .badge-strong { background-color: #EAF8F5; color: #16A58A; border: 1px solid #B2E7DC; }
    .badge-monitoring { background-color: #FEF8EC; color: #E6A52E; border: 1px solid #FBE5B7; }
    .badge-weak { background-color: #FDF1EC; color: #D9531E; border: 1px solid #F9D2C2; }
    .badge-repeated { background-color: #FDEBED; color: #E35D63; border: 1px solid #F7BAC0; }
    .badge-improving { background-color: #EAF3FF; color: #2878E5; border: 1px solid #BFDCFF; }
    .badge-declining { background-color: #FEF2E8; color: #DD6B20; border: 1px solid #FCD8B8; }
    .badge-insufficient { background-color: #F1F5F9; color: #64748B; border: 1px solid #E2EAF3; }

    /* Alert / Diagnostic Box */
    .gl-alert-box {
        background-color: #FFFFFF;
        border: 1px solid #E2EAF3;
        border-left: 4px solid #2878E5;
        border-radius: 4px;
        padding: 12px 16px;
        font-size: 0.88rem;
        color: #102B50;
        margin-bottom: 12px;
    }
    .gl-alert-box.critical {
        border-left-color: #E35D63;
        background-color: #FFF7F8;
    }
    .gl-alert-box.warning {
        border-left-color: #E6A52E;
        background-color: #FFFBF2;
    }
    .gl-alert-box.success {
        border-left-color: #16A58A;
        background-color: #F4FBF9;
    }

    /* Form Controls */
    input, select, textarea {
        border-radius: 4px !important;
        border: 1px solid #E2EAF3 !important;
        font-size: 0.86rem !important;
        color: #102B50 !important;
    }
    input:focus, select:focus, textarea:focus {
        border-color: #2878E5 !important;
        box-shadow: 0 0 0 1px #2878E5 !important;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E2EAF3 !important;
        border-radius: 4px !important;
        background-color: #FFFFFF !important;
    }

    /* File Uploader Clean Styling */
    [data-testid="stFileUploader"] {
        padding: 0 !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed #CBD5E1 !important;
        border-radius: 6px !important;
        background-color: #FFFFFF !important;
        padding: 1.25rem !important;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #2878E5 !important;
        background-color: #F8FAFC !important;
    }
</style>
"""


def get_badge_html(classification: str) -> str:
    """Returns clean styled HTML badge for weakness classifications without emojis."""
    cls_clean = classification.lower().replace(" ", "-")
    cls_map = {
        "strong": "badge-strong",
        "monitoring": "badge-monitoring",
        "good": "badge-monitoring",
        "weak": "badge-weak",
        "needs-revision": "badge-weak",
        "repeated-weakness": "badge-repeated",
        "critical": "badge-repeated",
        "improving": "badge-improving",
        "declining": "badge-declining",
        "insufficient-data": "badge-insufficient"
    }
    badge_class = cls_map.get(cls_clean, "badge-insufficient")
    return f'<span class="badge-pill {badge_class}">{classification}</span>'
