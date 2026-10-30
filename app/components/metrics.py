"""
GradeLens Professional UI Components & Metric Cards.
Implements clean, unindented, high-contrast components strictly following the design system.
No emojis, clean rectangular cards, restrained borders.
"""

import streamlit as st
from typing import Optional


def render_kpi_card(label: str, value: str, subtext: str = "", delta: Optional[str] = None):
    """
    Renders an understated, elegant commercial KPI card.
    Single-line HTML guarantees no Markdown indentation code-block bugs.
    """
    delta_badge = (
        f'<span style="background-color:#EAF8F5; color:#16A58A; padding:1px 6px; border-radius:3px; font-weight:600; font-size:0.75rem; border:1px solid #B2E7DC;">+{delta}</span>'
        if delta and not delta.startswith("-") else
        (f'<span style="background-color:#FDEBED; color:#E35D63; padding:1px 6px; border-radius:3px; font-weight:600; font-size:0.75rem; border:1px solid #F7BAC0;">{delta}</span>' if delta else "")
    )

    card_html = (
        f'<div class="gl-kpi-card">'
        f'<div class="gl-kpi-label">{label}</div>'
        f'<div class="gl-kpi-value">{value}</div>'
        f'<div class="gl-kpi-sub">{delta_badge} <span>{subtext}</span></div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_alert_box(title: str, text: str, alert_type: str = "info"):
    """
    Renders a clear alert/diagnostic notification.
    alert_type: 'info' (primary blue), 'warning' (amber), 'critical' (red), 'success' (teal).
    """
    css_class = "gl-alert-box"
    if alert_type == "critical":
        css_class += " critical"
    elif alert_type == "warning":
        css_class += " warning"
    elif alert_type == "success":
        css_class += " success"

    box_html = (
        f'<div class="{css_class}">'
        f'<div style="font-weight:700; font-size:0.9rem; margin-bottom:3px; color:#102B50;">{title}</div>'
        f'<div style="font-size:0.85rem; color:#475569; line-height:1.45;">{text}</div>'
        f'</div>'
    )
    st.markdown(box_html, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str = ""):
    """Renders a standard clean section heading."""
    header_html = f'<div class="gl-section-title"><span>{title}</span></div>'
    st.markdown(header_html, unsafe_allow_html=True)
    if subtitle:
        sub_html = f'<p style="color:#64748B; font-size:0.83rem; margin-top:-6px; margin-bottom:12px;">{subtitle}</p>'
        st.markdown(sub_html, unsafe_allow_html=True)


def render_reasoning_box(title: str, text: str, alert_type: str = "info"):
    """Alias for render_alert_box providing transparent analytical explanations."""
    render_alert_box(title, text, alert_type)


def render_progress_bar(label: str, percentage: float, score_text: str = "", color: str = "#2878E5"):
    """Renders a sleek linear progress indicator."""
    pct_clamped = max(0.0, min(100.0, percentage))
    html = (
        f'<div style="margin-bottom:10px;">'
        f'<div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:600; margin-bottom:4px; color:#102B50;">'
        f'<span>{label}</span>'
        f'<span style="color:#64748B;">{score_text if score_text else f"{pct_clamped:.1f}%"}</span>'
        f'</div>'
        f'<div style="width:100%; height:7px; background-color:#E2EAF3; border-radius:4px; overflow:hidden;">'
        f'<div style="width:{pct_clamped}%; height:100%; background-color:{color}; border-radius:4px;"></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
