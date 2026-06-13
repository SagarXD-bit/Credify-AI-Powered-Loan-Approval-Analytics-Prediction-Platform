"""
Credify — AI-Powered Loan Approval Analytics & Prediction Platform
Built with Streamlit, Pandas, Scikit-learn, Plotly, and SQLite.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.data_utils import (
    load_raw_data, clean_data, prepare_features,
    encode_single_input, get_missing_summary, FEATURE_COLS,
)
from utils.ml_utils import (
    train_and_evaluate, load_best_model, load_model_meta,
    predict_loan, get_feature_importances, get_decision_explanation,
)
from utils.db_utils import (
    init_db, save_prediction, get_predictions, get_summary_stats,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Credify — AI Loan Analytics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Global CSS — Credify design system
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Reset & base ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.main .block-container { padding: 2rem 2.5rem 1rem 2.5rem; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(200deg, #050e1f 0%, #0b1f3a 40%, #0f2d52 100%) !important;
    border-right: 1px solid rgba(99,179,237,0.15);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: #cbd5e0 !important; }
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap: 4px !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 14px !important; font-weight: 500 !important;
    padding: 10px 14px !important; border-radius: 8px !important;
    transition: all 0.2s ease !important; cursor: pointer !important;
    border: 1px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(99,179,237,0.12) !important;
    border-color: rgba(99,179,237,0.25) !important;
    color: #90cdf4 !important;
}

/* ── Brand hero (sidebar top) ── */
.brand-hero {
    background: linear-gradient(135deg, rgba(99,179,237,0.15) 0%, rgba(129,230,217,0.08) 100%);
    border-bottom: 1px solid rgba(99,179,237,0.2);
    padding: 28px 20px 22px 20px;
    margin-bottom: 8px;
    text-align: center;
}
.brand-logo {
    font-size: 32px; font-weight: 900; letter-spacing: -1px;
    background: linear-gradient(135deg, #63b3ed, #81e6d9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1; margin-bottom: 4px;
}
.brand-tm { font-size: 11px; vertical-align: super; opacity: 0.7; }
.brand-tagline {
    font-size: 10.5px; color: #718096 !important;
    text-transform: uppercase; letter-spacing: 1.2px; margin-top: 6px;
}

/* ── Sidebar stats widget ── */
.sidebar-stat-box {
    background: rgba(99,179,237,0.07);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 10px; padding: 14px 16px; margin: 10px 16px 4px 16px;
}
.sidebar-stat-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.sidebar-stat-label { font-size: 11px; color: #718096 !important; text-transform: uppercase; letter-spacing: 0.8px; }
.sidebar-stat-val { font-size: 18px; font-weight: 700; color: #90cdf4 !important; }
.sidebar-divider { border: none; border-top: 1px solid rgba(99,179,237,0.12); margin: 4px 0; }
.sidebar-mini { display: flex; justify-content: space-between; padding-top: 6px; }
.sidebar-mini-item { text-align: center; flex: 1; }
.sidebar-mini-val { font-size: 15px; font-weight: 600; }
.sidebar-mini-val.green { color: #68d391 !important; }
.sidebar-mini-val.red   { color: #fc8181 !important; }
.sidebar-mini-lbl { font-size: 10px; color: #718096 !important; text-transform: uppercase; }

/* ── Page header ── */
.page-header {
    display: flex; align-items: flex-start; gap: 14px;
    padding: 20px 24px; margin-bottom: 24px;
    background: linear-gradient(135deg, #ebf8ff 0%, #e6fffa 100%);
    border-radius: 14px; border-left: 5px solid #3182ce;
    box-shadow: 0 2px 12px rgba(49,130,206,0.08);
}
.page-header-icon { font-size: 36px; line-height: 1; }
.page-header-title { font-size: 26px; font-weight: 800; color: #1a365d; line-height: 1.2; margin: 0; }
.page-header-sub { font-size: 13px; color: #4a5568; margin-top: 4px; }

/* ── KPI cards ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }
.kpi-card {
    border-radius: 14px; padding: 22px 20px 18px 20px;
    color: white; position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.18); }
.kpi-card.blue   { background: linear-gradient(135deg, #2b6cb0 0%, #1a365d 100%); }
.kpi-card.green  { background: linear-gradient(135deg, #276749 0%, #1c4532 100%); }
.kpi-card.red    { background: linear-gradient(135deg, #c53030 0%, #742a2a 100%); }
.kpi-card.teal   { background: linear-gradient(135deg, #285e61 0%, #1d4044 100%); }
.kpi-card::after {
    content: ''; position: absolute; right: -20px; top: -20px;
    width: 100px; height: 100px; border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.kpi-icon { font-size: 22px; margin-bottom: 10px; opacity: 0.85; }
.kpi-value { font-size: 38px; font-weight: 900; letter-spacing: -2px; line-height: 1; }
.kpi-label { font-size: 11.5px; text-transform: uppercase; letter-spacing: 1.1px; opacity: 0.75; margin-top: 6px; }
.kpi-sub { font-size: 11px; opacity: 0.5; margin-top: 4px; }

/* ── Chart card ── */
.chart-card {
    background: white; border-radius: 14px; padding: 20px 20px 8px 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e2e8f0;
    margin-bottom: 16px;
}
.chart-title {
    font-size: 14px; font-weight: 700; color: #1a365d;
    text-transform: uppercase; letter-spacing: 0.8px;
    border-bottom: 2px solid #ebf8ff; padding-bottom: 10px; margin-bottom: 4px;
}

/* ── Section header ── */
.section-header {
    font-size: 17px; font-weight: 700; color: #1a365d;
    border-left: 4px solid #3182ce; padding-left: 12px;
    margin: 22px 0 14px 0; letter-spacing: -0.2px;
}

/* ── Metric badge ── */
.metric-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: 12px; font-weight: 600; margin: 2px;
}
.badge-blue  { background: #ebf8ff; color: #2b6cb0; }
.badge-green { background: #f0fff4; color: #276749; }
.badge-red   { background: #fff5f5; color: #c53030; }

/* ── Result cards ── */
.result-card {
    border-radius: 16px; padding: 28px 24px; text-align: center;
    margin-bottom: 10px; position: relative; overflow: hidden;
}
.result-card.approved {
    background: linear-gradient(135deg, #f0fff4 0%, #e6fffa 100%);
    border: 2px solid #68d391;
    box-shadow: 0 4px 20px rgba(104,211,145,0.2);
}
.result-card.rejected {
    background: linear-gradient(135deg, #fff5f5 0%, #ffe4e6 100%);
    border: 2px solid #fc8181;
    box-shadow: 0 4px 20px rgba(252,129,129,0.2);
}
.result-icon { font-size: 52px; margin-bottom: 10px; }
.result-label { font-size: 28px; font-weight: 900; letter-spacing: -1px; margin-bottom: 8px; }
.result-label.approved { color: #276749; }
.result-label.rejected { color: #c53030; }
.result-prob { font-size: 18px; font-weight: 600; color: #4a5568; }
.result-conf { display: inline-block; padding: 4px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-top: 10px; }
.conf-high   { background: #f0fff4; color: #276749; border: 1px solid #9ae6b4; }
.conf-med    { background: #fffff0; color: #744210; border: 1px solid #faf089; }
.conf-low    { background: #fff5f5; color: #c53030; border: 1px solid #feb2b2; }

/* ── Explanation card ── */
.explain-card {
    background: linear-gradient(135deg, #ebf8ff 0%, #e6fffa 100%);
    border-radius: 12px; padding: 16px 18px; margin-bottom: 8px;
    border-left: 4px solid #3182ce;
    font-size: 14px; color: #2d3748; line-height: 1.6;
}

/* ── Model card ── */
.model-best-banner {
    background: linear-gradient(135deg, #1a365d 0%, #2b6cb0 100%);
    border-radius: 12px; padding: 14px 20px; color: white;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 20px; box-shadow: 0 4px 16px rgba(43,108,176,0.3);
}
.model-best-icon { font-size: 28px; }
.model-best-name { font-size: 20px; font-weight: 800; letter-spacing: -0.5px; }
.model-best-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.7; }

/* ── Footer / trademark ── */
.credify-footer {
    margin-top: 48px; padding: 28px 0 12px 0;
    border-top: 1px solid #e2e8f0; text-align: center;
}
.footer-logo {
    font-size: 20px; font-weight: 900; letter-spacing: -0.5px;
    background: linear-gradient(135deg, #2b6cb0, #285e61);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}
.footer-tagline { font-size: 11px; color: #a0aec0; letter-spacing: 1.5px; text-transform: uppercase; margin-top: 4px; }
.footer-copy { font-size: 11px; color: #718096; margin-top: 8px; }
.footer-badges { margin-top: 10px; display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.footer-badge {
    font-size: 10px; padding: 3px 10px; border-radius: 20px;
    background: #edf2f7; color: #4a5568; border: 1px solid #e2e8f0;
}

/* ── Table overrides ── */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0 !important; font-weight: 600 !important;
    font-size: 13px !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2b6cb0 0%, #1a365d 100%) !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 14px !important;
    padding: 12px 24px !important; letter-spacing: 0.2px !important;
    box-shadow: 0 4px 14px rgba(43,108,176,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(43,108,176,0.45) !important;
}

/* ── Form submit button ── */
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(135deg, #276749 0%, #1c4532 100%) !important;
    border: none !important; border-radius: 10px !important;
    font-weight: 700 !important; font-size: 15px !important; color: white !important;
    box-shadow: 0 4px 14px rgba(39,103,73,0.35) !important;
}

/* ── Alerts ── */
.stAlert { border-radius: 10px !important; }

/* ── Sidebar nav section label ── */
.nav-section-label {
    font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px;
    color: #4a5568 !important; padding: 14px 16px 6px 16px; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Init DB
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-hero">
        <div class="brand-logo">Credify<span class="brand-tm">™</span></div>
        <div class="brand-tagline">AI Loan Intelligence Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-section-label">Navigation</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        options=[
            "📊  Dashboard",
            "📁  Data Management",
            "🤖  Machine Learning",
            "💳  Loan Prediction",
            "📜  Prediction History",
        ],
        label_visibility="collapsed",
    )

    db_stats = get_summary_stats()
    total_pred = db_stats["total"]
    appr = db_stats["approved"]
    rej  = db_stats["rejected"]
    pred_rate = round(appr / total_pred * 100, 1) if total_pred else 0

    st.markdown(f"""
    <div class="sidebar-stat-box">
        <div class="sidebar-stat-row">
            <span class="sidebar-stat-label">Live Predictions</span>
        </div>
        <div class="sidebar-stat-val">{total_pred:,}</div>
        <hr class="sidebar-divider">
        <div class="sidebar-mini">
            <div class="sidebar-mini-item">
                <div class="sidebar-mini-val green">{appr}</div>
                <div class="sidebar-mini-lbl">Approved</div>
            </div>
            <div class="sidebar-mini-item" style="border-left:1px solid rgba(99,179,237,0.15)">
                <div class="sidebar-mini-val red">{rej}</div>
                <div class="sidebar-mini-lbl">Rejected</div>
            </div>
            <div class="sidebar-mini-item" style="border-left:1px solid rgba(99,179,237,0.15)">
                <div class="sidebar-mini-val" style="color:#90cdf4 !important">{pred_rate}%</div>
                <div class="sidebar-mini-lbl">Rate</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:16px;margin-top:auto">
        <div style="font-size:10px;color:#4a5568;text-align:center;line-height:1.8">
            Powered by Random Forest · Decision Tree · Logistic Regression<br>
            <span style="color:#2d3748;font-weight:600">Credify™</span> v1.0 · 2026
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data(uploaded=None):
    raw = load_raw_data(uploaded)
    cleaned = clean_data(raw)
    return raw, cleaned


def page_header(icon, title, subtitle):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-header-icon">{icon}</div>
        <div>
            <div class="page-header-title">{title}</div>
            <div class="page-header-sub">{subtitle}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_header(text):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)


def credify_footer():
    st.markdown("""
    <div class="credify-footer">
        <div class="footer-logo">Credify™</div>
        <div class="footer-tagline">AI-Powered Loan Approval Analytics &amp; Prediction Platform</div>
        <div class="footer-badges">
            <span class="footer-badge">🤖 Machine Learning</span>
            <span class="footer-badge">📊 Real-time Analytics</span>
            <span class="footer-badge">🔒 Secure &amp; Private</span>
            <span class="footer-badge">🐍 Python · Streamlit · Scikit-learn</span>
        </div>
        <div class="footer-copy">
            © 2026 <strong>Credify™</strong> · All Rights Reserved ·
            Credify is a trademark. Unauthorized reproduction is prohibited.<br>
            Built with ❤️ · Designed for portfolio excellence
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════
if page == "📊  Dashboard":
    page_header("📊", "Analytics Dashboard",
                "Interactive overview of loan application patterns, approval trends, and demographic insights.")

    try:
        raw_df, df = get_data()
    except FileNotFoundError:
        st.warning("Dataset not found. Please upload a CSV on the Data Management page.")
        st.stop()

    total  = len(df)
    approved = int((df["Loan_Status"] == "Y").sum()) if "Loan_Status" in df.columns else 0
    rejected = total - approved
    rate   = round(approved / total * 100, 1) if total else 0
    avg_loan = round(df["LoanAmount"].mean(), 1) if "LoanAmount" in df.columns else 0

    # ── KPI row ──
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card blue">
            <div class="kpi-icon">📋</div>
            <div class="kpi-value">{total:,}</div>
            <div class="kpi-label">Total Applications</div>
            <div class="kpi-sub">Dataset records</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-icon">✅</div>
            <div class="kpi-value">{approved:,}</div>
            <div class="kpi-label">Approved Loans</div>
            <div class="kpi-sub">{rate}% of all applications</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-icon">❌</div>
            <div class="kpi-value">{rejected:,}</div>
            <div class="kpi-label">Rejected Loans</div>
            <div class="kpi-sub">{round(100-rate,1)}% of all applications</div>
        </div>
        <div class="kpi-card teal">
            <div class="kpi-icon">💰</div>
            <div class="kpi-value">{avg_loan}K</div>
            <div class="kpi-label">Avg Loan Amount</div>
            <div class="kpi-sub">₹ thousands</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 1 ──
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-card"><div class="chart-title">Approval by Credit History</div>', unsafe_allow_html=True)
        ch = df.groupby(["Credit_History", "Loan_Status"]).size().reset_index(name="Count")
        ch["Credit_History"] = ch["Credit_History"].map({1.0: "Good Credit", 0.0: "No Credit"}).fillna("Unknown")
        ch["Loan_Status"] = ch["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig = px.bar(ch, x="Credit_History", y="Count", color="Loan_Status", barmode="group",
                     color_discrete_map={"Approved": "#276749", "Rejected": "#c53030"})
        fig.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                          paper_bgcolor="white", legend_title="", font_family="Inter",
                          height=260, legend=dict(orientation="h", y=-0.15))
        fig.update_xaxes(showgrid=False); fig.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="chart-card"><div class="chart-title">Approval by Education Level</div>', unsafe_allow_html=True)
        ed = df.groupby(["Education", "Loan_Status"]).size().reset_index(name="Count")
        ed["Loan_Status"] = ed["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig2 = px.bar(ed, x="Education", y="Count", color="Loan_Status", barmode="group",
                      color_discrete_map={"Approved": "#2b6cb0", "Rejected": "#c53030"})
        fig2.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                           paper_bgcolor="white", legend_title="", font_family="Inter",
                           height=260, legend=dict(orientation="h", y=-0.15))
        fig2.update_xaxes(showgrid=False); fig2.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 2 ──
    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="chart-card"><div class="chart-title">Approval by Property Area</div>', unsafe_allow_html=True)
        pa = df.groupby(["Property_Area", "Loan_Status"]).size().reset_index(name="Count")
        pa["Loan_Status"] = pa["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig3 = px.bar(pa, x="Property_Area", y="Count", color="Loan_Status", barmode="stack",
                      color_discrete_map={"Approved": "#285e61", "Rejected": "#c53030"})
        fig3.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                           paper_bgcolor="white", legend_title="", font_family="Inter",
                           height=260, legend=dict(orientation="h", y=-0.15))
        fig3.update_xaxes(showgrid=False); fig3.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="chart-card"><div class="chart-title">Applicant Income Distribution</div>', unsafe_allow_html=True)
        fig4 = px.histogram(df, x="ApplicantIncome", nbins=40, color_discrete_sequence=["#2b6cb0"],
                            labels={"ApplicantIncome": "Monthly Income (₹)"})
        fig4.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                           paper_bgcolor="white", showlegend=False, font_family="Inter", height=260)
        fig4.update_xaxes(showgrid=False); fig4.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Row 3 ──
    col5, col6 = st.columns(2)
    with col5:
        st.markdown('<div class="chart-card"><div class="chart-title">Loan Amount by Approval Status</div>', unsafe_allow_html=True)
        fig5 = px.violin(df, x="Loan_Status", y="LoanAmount", color="Loan_Status", box=True,
                         color_discrete_map={"Y": "#276749", "N": "#c53030"},
                         labels={"Loan_Status": "Decision", "LoanAmount": "Loan Amount (₹K)"})
        fig5.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                           paper_bgcolor="white", showlegend=False, font_family="Inter", height=260)
        fig5.update_xaxes(showgrid=False); fig5.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="chart-card"><div class="chart-title">Approval Rate by Gender &amp; Marital Status</div>', unsafe_allow_html=True)
        gm = df.groupby(["Gender", "Married"])["Loan_Status"].apply(
            lambda s: round((s == "Y").sum() / len(s) * 100, 1)
        ).reset_index(name="Approval Rate (%)")
        gm["Segment"] = gm["Gender"] + " · " + gm["Married"].map({"Yes": "Married", "No": "Single"})
        fig6 = px.bar(gm, x="Segment", y="Approval Rate (%)", color="Segment",
                      color_discrete_sequence=["#2b6cb0", "#276749", "#744210", "#285e61"])
        fig6.update_layout(margin=dict(t=4, b=4, l=0, r=0), plot_bgcolor="white",
                           paper_bgcolor="white", showlegend=False, font_family="Inter", height=260)
        fig6.update_traces(texttemplate="%{y}%", textposition="outside")
        fig6.update_xaxes(showgrid=False); fig6.update_yaxes(gridcolor="#f0f4f8", range=[0, 110])
        st.plotly_chart(fig6, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    credify_footer()


# ══════════════════════════════════════════════
# PAGE 2 — DATA MANAGEMENT
# ══════════════════════════════════════════════
elif page == "📁  Data Management":
    page_header("📁", "Data Management",
                "Load, inspect, validate, and clean your loan applicant dataset before training.")

    uploaded = st.file_uploader(
        "Upload a custom CSV dataset",
        type=["csv"],
        help="Columns required: Gender, Married, Dependents, Education, Self_Employed, "
             "ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, "
             "Credit_History, Property_Area, Loan_Status",
    )

    try:
        raw_df, df = get_data(uploaded)
    except FileNotFoundError:
        st.error("Default dataset not found. Please upload a CSV file above.")
        st.stop()

    # Summary row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", f"{len(df):,}")
    m2.metric("Columns", len(df.columns))
    m3.metric("Missing Values", int(raw_df.isnull().sum().sum()))
    m4.metric("Approved", f"{int((df.get('Loan_Status', pd.Series()) == 'Y').sum()):,}")

    st.markdown("")

    tab1, tab2, tab3 = st.tabs(["📋  Raw Data", "🧹  Cleaned Data", "📈  Data Quality"])

    with tab1:
        st.markdown(f"<small style='color:#718096'>Showing {len(raw_df):,} records — original, unmodified dataset</small>", unsafe_allow_html=True)
        st.dataframe(raw_df, use_container_width=True, height=400)

    with tab2:
        st.markdown(f"<small style='color:#718096'>{len(df):,} records after auto-cleaning (missing values imputed, types fixed)</small>", unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=400)
        st.download_button(
            "⬇️  Download Cleaned CSV",
            data=df.to_csv(index=False),
            file_name="credify_loan_cleaned.csv",
            mime="text/csv",
            type="primary",
        )

    with tab3:
        section_header("Missing Value Analysis")
        missing = get_missing_summary(raw_df)
        if missing.empty:
            st.success("✅ No missing values — your dataset is clean and ready for training.")
        else:
            c_a, c_b = st.columns([1, 2])
            with c_a:
                st.dataframe(missing, use_container_width=True)
            with c_b:
                fig_m = px.bar(missing.reset_index(), x="index", y="Missing %",
                               labels={"index": "Column", "Missing %": "Missing (%)"},
                               color_discrete_sequence=["#c53030"])
                fig_m.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                    font_family="Inter", height=240, margin=dict(t=4,b=4,l=0,r=0))
                st.plotly_chart(fig_m, use_container_width=True)

        section_header("Statistical Summary")
        st.dataframe(df.describe(include="all").T, use_container_width=True)

    credify_footer()


# ══════════════════════════════════════════════
# PAGE 3 — MACHINE LEARNING
# ══════════════════════════════════════════════
elif page == "🤖  Machine Learning":
    page_header("🤖", "Machine Learning Models",
                "Train, benchmark, and auto-select the best classifier — Credify's prediction engine.")

    try:
        raw_df, df = get_data()
    except FileNotFoundError:
        st.warning("Dataset not found. Please upload one on the Data Management page.")
        st.stop()

    if "Loan_Status" not in df.columns:
        st.error("Dataset must contain a 'Loan_Status' column to train models.")
        st.stop()

    train_col, info_col = st.columns([1, 2])
    with train_col:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.markdown("**Training Configuration**")
        test_size = st.slider("Test split ratio", 0.10, 0.40, 0.20, 0.05,
                              help="Proportion of data held out for evaluation")
        st.caption(f"Training rows: **{int(len(df)*(1-test_size)):,}** · Test rows: **{int(len(df)*test_size):,}**")
        train_btn = st.button("🚀  Train All Models", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with info_col:
        st.markdown("""
        <div class="chart-card">
            <div style="font-weight:700;color:#1a365d;margin-bottom:10px">Models in this run</div>
            <div style="display:flex;gap:12px;flex-wrap:wrap">
                <div style="flex:1;min-width:140px;background:#ebf8ff;border-radius:10px;padding:12px">
                    <div style="font-weight:700;color:#2b6cb0;font-size:13px">📈 Logistic Regression</div>
                    <div style="font-size:11px;color:#4a5568;margin-top:4px">Fast linear baseline · max_iter=1000</div>
                </div>
                <div style="flex:1;min-width:140px;background:#f0fff4;border-radius:10px;padding:12px">
                    <div style="font-weight:700;color:#276749;font-size:13px">🌿 Decision Tree</div>
                    <div style="font-size:11px;color:#4a5568;margin-top:4px">Interpretable · max_depth=6</div>
                </div>
                <div style="flex:1;min-width:140px;background:#fffff0;border-radius:10px;padding:12px">
                    <div style="font-weight:700;color:#744210;font-size:13px">🌳 Random Forest</div>
                    <div style="font-size:11px;color:#4a5568;margin-top:4px">100 estimators · max_depth=8</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    meta = load_model_meta()
    if meta and not train_btn:
        st.info(f"ℹ️ Showing last training session results — best model was **{meta['best_model_name']}**. Retrain anytime.")

    if train_btn:
        with st.spinner("⚙️  Training all three models on your dataset…"):
            X, y, _, _ = prepare_features(df)
            results, best_name = train_and_evaluate(X, y, test_size=test_size)
            st.session_state["ml_results"] = results
            st.session_state["best_name"] = best_name
        st.success(f"✅ Training complete! Best model selected: **{best_name}**")
        meta = load_model_meta()

    if meta:
        st.markdown(f"""
        <div class="model-best-banner">
            <div class="model-best-icon">⭐</div>
            <div>
                <div class="model-best-label">Best Model: {meta['best_model_name']}</div>
                <div class="model-best-name" style="font-size:13px;opacity:0.75">
                    Saved to disk · Used for all predictions
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        records = []
        for model_name, m in meta["metrics"].items():
            is_best = model_name == meta["best_model_name"]
            records.append({
                "Model": ("⭐ " if is_best else "") + model_name,
                "Accuracy":  f"{m['accuracy']:.2%}",
                "Precision": f"{m['precision']:.2%}",
                "Recall":    f"{m['recall']:.2%}",
                "F1 Score":  f"{m['f1']:.2%}",
            })

        section_header("Model Performance Comparison")
        st.dataframe(pd.DataFrame(records).set_index("Model"), use_container_width=True)

        metric_df = pd.DataFrame([
            {"Model": n, "Accuracy": m["accuracy"], "Precision": m["precision"],
             "Recall": m["recall"], "F1 Score": m["f1"]}
            for n, m in meta["metrics"].items()
        ])
        fig_comp = px.bar(
            metric_df.melt(id_vars="Model", var_name="Metric", value_name="Score"),
            x="Metric", y="Score", color="Model", barmode="group",
            color_discrete_sequence=["#2b6cb0", "#276749", "#744210"],
            range_y=[0, 1],
        )
        fig_comp.update_traces(texttemplate="%{y:.1%}", textposition="outside")
        fig_comp.update_layout(
            plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
            yaxis_tickformat=".0%", legend_title="",
            margin=dict(t=10, b=10, l=0, r=0), height=320,
        )
        fig_comp.update_xaxes(showgrid=False); fig_comp.update_yaxes(gridcolor="#f0f4f8")
        st.plotly_chart(fig_comp, use_container_width=True)

        if "ml_results" in st.session_state:
            section_header("Confusion Matrices")
            cms = st.columns(3)
            for idx, (model_name, res) in enumerate(st.session_state["ml_results"].items()):
                cm = np.array(res["confusion_matrix"])
                fig_cm = px.imshow(
                    cm,
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=["Rejected", "Approved"], y=["Rejected", "Approved"],
                    text_auto=True, color_continuous_scale="Blues",
                    title=model_name,
                )
                fig_cm.update_layout(margin=dict(t=40, b=10), font_family="Inter",
                                     height=260, paper_bgcolor="white")
                cms[idx].plotly_chart(fig_cm, use_container_width=True)

        model = load_best_model()
        if model:
            section_header("Feature Importances — Best Model")
            imp_df = get_feature_importances(model, meta.get("feature_names", FEATURE_COLS))
            if imp_df is not None:
                fig_imp = px.bar(imp_df, x="Importance", y="Feature", orientation="h",
                                 color="Importance", color_continuous_scale="Blues")
                fig_imp.update_layout(
                    plot_bgcolor="white", paper_bgcolor="white", font_family="Inter",
                    yaxis=dict(autorange="reversed"), margin=dict(t=4, b=4, l=0, r=0),
                    height=max(250, len(imp_df) * 32),
                )
                st.plotly_chart(fig_imp, use_container_width=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#718096">
            <div style="font-size:48px;margin-bottom:12px">🤖</div>
            <div style="font-size:18px;font-weight:600;color:#4a5568">No models trained yet</div>
            <div style="font-size:14px;margin-top:6px">Click <b>Train All Models</b> to begin</div>
        </div>
        """, unsafe_allow_html=True)

    credify_footer()


# ══════════════════════════════════════════════
# PAGE 4 — LOAN PREDICTION
# ══════════════════════════════════════════════
elif page == "💳  Loan Prediction":
    page_header("💳", "Loan Prediction",
                "Enter applicant details below and get an instant AI-powered approval decision with explanation.")

    model = load_best_model()
    meta  = load_model_meta()

    if model is None:
        st.warning("⚠️  No trained model found. Go to **Machine Learning** and click **Train All Models** first.")
        st.stop()

    model_name = meta["best_model_name"] if meta else "Best Model"
    st.markdown(f"""
    <div style="display:inline-flex;align-items:center;gap:8px;
                background:#ebf8ff;border:1px solid #bee3f8;border-radius:8px;
                padding:8px 14px;margin-bottom:20px;font-size:13px;color:#2b6cb0;font-weight:600">
        ⭐ Active Model: {model_name}
    </div>
    """, unsafe_allow_html=True)

    with st.form("prediction_form"):
        section_header("Personal Information")
        c1, c2, c3 = st.columns(3)
        with c1:
            gender      = st.selectbox("Gender", ["Male", "Female"])
            married     = st.selectbox("Marital Status", ["Yes", "No"])
            dependents  = st.selectbox("Number of Dependents", ["0", "1", "2", "3+"])
        with c2:
            education      = st.selectbox("Education", ["Graduate", "Not Graduate"])
            self_employed  = st.selectbox("Employment Type", ["No", "Yes"],
                                          format_func=lambda x: "Salaried" if x == "No" else "Self-Employed")
            property_area  = st.selectbox("Property Location", ["Urban", "Semiurban", "Rural"])
        with c3:
            credit_history = st.selectbox("Credit History", [1, 0],
                                          format_func=lambda x: "✅ Good (meets guidelines)" if x == 1 else "❌ None / Poor")
            loan_amount_term = st.selectbox(
                "Loan Repayment Term",
                [360, 180, 120, 240, 300, 480, 60, 36, 84],
                format_func=lambda x: f"{x} months  ({x // 12} yrs)" if x >= 12 else f"{x} months",
            )

        section_header("Financial Details")
        f1, f2, f3 = st.columns(3)
        with f1:
            applicant_income    = st.number_input("Applicant Monthly Income (₹)", min_value=0, value=5000, step=500)
        with f2:
            coapplicant_income  = st.number_input("Co-applicant Monthly Income (₹)", min_value=0, value=0, step=500)
        with f3:
            loan_amount         = st.number_input("Requested Loan Amount (₹ thousands)", min_value=1, value=150, step=10)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("🔍  Analyse & Predict Loan Approval", type="primary", use_container_width=True)

    if submitted:
        applicant_data = {
            "Gender": gender, "Married": married, "Dependents": dependents,
            "Education": education, "Self_Employed": self_employed,
            "ApplicantIncome": applicant_income, "CoapplicantIncome": coapplicant_income,
            "LoanAmount": loan_amount, "Loan_Amount_Term": loan_amount_term,
            "Credit_History": credit_history, "Property_Area": property_area,
        }

        feature_vector = encode_single_input(applicant_data)
        prediction, probability, confidence = predict_loan(model, feature_vector)
        approved = prediction == "Approved"

        save_prediction(applicant_data, prediction, probability, model_name)

        st.markdown("---")
        st.markdown('<div class="section-header">Prediction Result</div>', unsafe_allow_html=True)

        res_col, gauge_col = st.columns([1, 1])

        with res_col:
            card_class = "approved" if approved else "rejected"
            icon       = "✅" if approved else "🚫"
            color_cls  = "approved" if approved else "rejected"
            pct        = round(probability * 100, 1)
            conf_css   = {"High": "conf-high", "Medium": "conf-med", "Low": "conf-low"}[confidence]
            st.markdown(f"""
            <div class="result-card {card_class}">
                <div class="result-icon">{icon}</div>
                <div class="result-label {color_cls}">Loan {prediction}</div>
                <div class="result-prob">Approval Probability: <b>{pct}%</b></div>
                <div class="result-conf {conf_css}">{confidence} Confidence</div>
            </div>
            """, unsafe_allow_html=True)

        with gauge_col:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=round(probability * 100, 1),
                delta={"reference": 50, "valueformat": ".1f"},
                title={"text": "Approval Score", "font": {"family": "Inter", "size": 15}},
                number={"suffix": "%", "font": {"family": "Inter", "size": 36}},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#e2e8f0"},
                    "bar": {"color": "#276749" if approved else "#c53030", "thickness": 0.28},
                    "bgcolor": "white",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40],  "color": "#fff5f5"},
                        {"range": [40, 60], "color": "#fffff0"},
                        {"range": [60, 100],"color": "#f0fff4"},
                    ],
                    "threshold": {
                        "line": {"color": "#2b6cb0", "width": 3},
                        "thickness": 0.75, "value": 50,
                    },
                },
            ))
            fig_gauge.update_layout(
                height=260, margin=dict(t=30, b=10, l=20, r=20),
                paper_bgcolor="white", font_family="Inter",
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        section_header("Why This Decision? — Key Factors")
        feature_names = meta.get("feature_names", list(applicant_data.keys())) if meta else list(applicant_data.keys())
        explanations  = get_decision_explanation(feature_vector, feature_names, model)
        for exp in explanations:
            st.markdown(f'<div class="explain-card">{exp}</div>', unsafe_allow_html=True)

        with st.expander("📋  View Full Applicant Profile"):
            summary = pd.DataFrame([applicant_data]).T
            summary.columns = ["Value"]
            st.dataframe(summary, use_container_width=True)

    credify_footer()


# ══════════════════════════════════════════════
# PAGE 5 — PREDICTION HISTORY
# ══════════════════════════════════════════════
elif page == "📜  Prediction History":
    page_header("📜", "Prediction History",
                "Review, filter, and export all loan decisions made by the Credify prediction engine.")

    db_stats = get_summary_stats()
    appr = db_stats["approved"]
    rej  = db_stats["rejected"]
    tot  = db_stats["total"]
    hist_rate = round(appr / tot * 100, 1) if tot else 0

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card blue">
            <div class="kpi-icon">🗂️</div>
            <div class="kpi-value">{tot:,}</div>
            <div class="kpi-label">Total Predictions</div>
            <div class="kpi-sub">All time</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-icon">✅</div>
            <div class="kpi-value">{appr:,}</div>
            <div class="kpi-label">Approved</div>
            <div class="kpi-sub">{hist_rate}% approval rate</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-icon">❌</div>
            <div class="kpi-value">{rej:,}</div>
            <div class="kpi-label">Rejected</div>
            <div class="kpi-sub">{round(100 - hist_rate, 1)}% rejection rate</div>
        </div>
        <div class="kpi-card teal">
            <div class="kpi-icon">📅</div>
            <div class="kpi-value">{tot:,}</div>
            <div class="kpi-label">Total Sessions</div>
            <div class="kpi-sub">Credify AI engine</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([2, 1, 1])
    with sc1:
        search = st.text_input("🔍  Search records…", placeholder="e.g. Male, Urban, Approved, High…")
    with sc2:
        filter_pred = st.selectbox("Outcome", ["All", "Approved", "Rejected"])
    with sc3:
        filter_conf = st.selectbox("Confidence", ["All", "High", "Medium", "Low"])

    df_hist = get_predictions(search)
    if filter_pred != "All":
        df_hist = df_hist[df_hist["prediction"] == filter_pred]
    if filter_conf != "All":
        df_hist = df_hist[df_hist["confidence"] == filter_conf]

    if df_hist.empty:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#718096">
            <div style="font-size:48px;margin-bottom:12px">📭</div>
            <div style="font-size:18px;font-weight:600;color:#4a5568">No predictions found</div>
            <div style="font-size:14px;margin-top:6px">
                Make your first prediction on the <b>Loan Prediction</b> page
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        display_cols = ["id", "timestamp", "gender", "married", "education", "property_area",
                        "applicant_income", "loan_amount", "credit_history",
                        "prediction", "probability", "confidence", "model_used"]
        show_cols = [c for c in display_cols if c in df_hist.columns]

        def row_style(row):
            color = "#f0fff4" if row["prediction"] == "Approved" else "#fff5f5"
            return [f"background-color:{color}"] * len(row)

        styled = df_hist[show_cols].style.apply(row_style, axis=1)
        st.dataframe(styled, use_container_width=True, height=400)

        dl_col, _, _ = st.columns([1, 1, 1])
        with dl_col:
            st.download_button(
                "⬇️  Export as CSV",
                data=df_hist.to_csv(index=False),
                file_name="credify_prediction_history.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True,
            )

        if len(df_hist) > 1:
            section_header("History Analytics")
            hc1, hc2 = st.columns(2)

            with hc1:
                pie = df_hist["prediction"].value_counts().reset_index()
                pie.columns = ["Outcome", "Count"]
                fig_pie = px.pie(pie, names="Outcome", values="Count",
                                 color="Outcome",
                                 color_discrete_map={"Approved": "#276749", "Rejected": "#c53030"},
                                 hole=0.45)
                fig_pie.update_traces(textinfo="label+percent", textfont_size=13)
                fig_pie.update_layout(margin=dict(t=10, b=10), paper_bgcolor="white",
                                      font_family="Inter", showlegend=False, height=280)
                st.plotly_chart(fig_pie, use_container_width=True)

            with hc2:
                fig_prob = px.histogram(df_hist, x="probability", nbins=20,
                                        color_discrete_sequence=["#2b6cb0"],
                                        labels={"probability": "Approval Probability"},
                                        title="Score Distribution")
                fig_prob.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                                       font_family="Inter", margin=dict(t=30, b=4, l=0, r=0), height=280)
                fig_prob.update_xaxes(showgrid=False); fig_prob.update_yaxes(gridcolor="#f0f4f8")
                st.plotly_chart(fig_prob, use_container_width=True)

    credify_footer()
