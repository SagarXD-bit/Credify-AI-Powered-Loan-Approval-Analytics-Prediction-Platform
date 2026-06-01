"""
Loan Approval Prediction & Analytics Web Application
Built with Streamlit, Pandas, Scikit-learn, Plotly, and SQLite.
"""

import os
import sys

# Ensure utils package is importable
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
# Page config & theme
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LoanSense — Loan Approval Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS — professional banking theme
st.markdown("""
<style>
/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a2342 0%, #1a3a5c 100%);
}
[data-testid="stSidebar"] * { color: #e8f0fe !important; }
[data-testid="stSidebar"] .stRadio label { font-size: 15px !important; }

/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%);
    border-radius: 12px;
    padding: 20px 24px;
    color: white;
    text-align: center;
    box-shadow: 0 4px 15px rgba(13,71,161,0.25);
    margin-bottom: 8px;
}
.kpi-card.green  { background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%); box-shadow: 0 4px 15px rgba(46,125,50,0.25); }
.kpi-card.red    { background: linear-gradient(135deg, #c62828 0%, #b71c1c 100%); box-shadow: 0 4px 15px rgba(198,40,40,0.25); }
.kpi-card.purple { background: linear-gradient(135deg, #6a1b9a 0%, #4a148c 100%); box-shadow: 0 4px 15px rgba(106,27,154,0.25); }
.kpi-value { font-size: 36px; font-weight: 800; letter-spacing: -1px; }
.kpi-label { font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85; margin-top: 4px; }

/* ── Result badge ── */
.result-approved {
    background: #e8f5e9; border: 2px solid #43a047;
    border-radius: 10px; padding: 20px; text-align: center;
}
.result-rejected {
    background: #ffebee; border: 2px solid #e53935;
    border-radius: 10px; padding: 20px; text-align: center;
}
.result-title { font-size: 28px; font-weight: 800; margin-bottom: 6px; }

/* ── Section header ── */
.section-header {
    font-size: 22px; font-weight: 700; color: #0a2342;
    border-left: 4px solid #1565c0; padding-left: 12px;
    margin: 16px 0 12px 0;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Initialise DB on every cold start
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# Sidebar navigation
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏦 LoanSense")
    st.markdown("*AI-Powered Loan Decision Platform*")
    st.markdown("---")

    page = st.radio(
        "Navigate",
        options=[
            "📊 Dashboard",
            "📁 Data Management",
            "🤖 Machine Learning",
            "💳 Loan Prediction",
            "📜 Prediction History",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    db_stats = get_summary_stats()
    st.markdown(f"**Predictions Made:** {db_stats['total']}")
    st.markdown(f"**Approvals:** {db_stats['approved']}  |  **Rejections:** {db_stats['rejected']}")

# ─────────────────────────────────────────────
# Helper: cached data loader
# ─────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data(uploaded=None):
    raw = load_raw_data(uploaded)
    cleaned = clean_data(raw)
    return raw, cleaned


# ══════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ══════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Analytics Dashboard")
    st.caption("Interactive overview of loan application patterns and approval trends.")

    try:
        raw_df, df = get_data()
    except FileNotFoundError:
        st.warning("Dataset not found. Please upload a CSV on the Data Management page.")
        st.stop()

    total = len(df)
    approved = int((df["Loan_Status"] == "Y").sum()) if "Loan_Status" in df.columns else 0
    rejected = total - approved
    rate = round(approved / total * 100, 1) if total else 0

    # ── KPI row ──
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{total:,}</div>
        <div class="kpi-label">Total Applications</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card green"><div class="kpi-value">{approved:,}</div>
        <div class="kpi-label">Approved Loans</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card red"><div class="kpi-value">{rejected:,}</div>
        <div class="kpi-label">Rejected Loans</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card purple"><div class="kpi-value">{rate}%</div>
        <div class="kpi-label">Approval Rate</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Row 1: Credit History & Education ──
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Approval by Credit History</div>', unsafe_allow_html=True)
        ch = df.groupby(["Credit_History", "Loan_Status"]).size().reset_index(name="Count")
        ch["Credit_History"] = ch["Credit_History"].map({1: "Good Credit", 0: "No Credit"}).fillna("Unknown")
        ch["Loan_Status"] = ch["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig = px.bar(ch, x="Credit_History", y="Count", color="Loan_Status",
                     barmode="group",
                     color_discrete_map={"Approved": "#2e7d32", "Rejected": "#c62828"})
        fig.update_layout(margin=dict(t=10, b=10), legend_title="Decision", plot_bgcolor="white")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Approval by Education</div>', unsafe_allow_html=True)
        ed = df.groupby(["Education", "Loan_Status"]).size().reset_index(name="Count")
        ed["Loan_Status"] = ed["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig2 = px.bar(ed, x="Education", y="Count", color="Loan_Status",
                      barmode="group",
                      color_discrete_map={"Approved": "#1565c0", "Rejected": "#c62828"})
        fig2.update_layout(margin=dict(t=10, b=10), legend_title="Decision", plot_bgcolor="white")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Row 2: Property Area & Income Distribution ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="section-header">Approval by Property Area</div>', unsafe_allow_html=True)
        pa = df.groupby(["Property_Area", "Loan_Status"]).size().reset_index(name="Count")
        pa["Loan_Status"] = pa["Loan_Status"].map({"Y": "Approved", "N": "Rejected"})
        fig3 = px.bar(pa, x="Property_Area", y="Count", color="Loan_Status",
                      barmode="stack",
                      color_discrete_map={"Approved": "#0288d1", "Rejected": "#e64a19"})
        fig3.update_layout(margin=dict(t=10, b=10), legend_title="Decision", plot_bgcolor="white")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<div class="section-header">Applicant Income Distribution</div>', unsafe_allow_html=True)
        fig4 = px.histogram(df, x="ApplicantIncome", nbins=40, color_discrete_sequence=["#1565c0"],
                            labels={"ApplicantIncome": "Income (₹)"})
        fig4.update_layout(margin=dict(t=10, b=10), plot_bgcolor="white", showlegend=False)
        st.plotly_chart(fig4, use_container_width=True)

    # ── Row 3: Loan Amount & Gender / Marital ──
    col5, col6 = st.columns(2)

    with col5:
        st.markdown('<div class="section-header">Loan Amount Distribution</div>', unsafe_allow_html=True)
        fig5 = px.box(df, x="Loan_Status", y="LoanAmount",
                      color="Loan_Status",
                      color_discrete_map={"Y": "#2e7d32", "N": "#c62828"},
                      labels={"Loan_Status": "Decision", "LoanAmount": "Loan Amount (₹K)"})
        fig5.update_layout(margin=dict(t=10, b=10), plot_bgcolor="white", showlegend=False)
        st.plotly_chart(fig5, use_container_width=True)

    with col6:
        st.markdown('<div class="section-header">Approval Rate by Gender & Marital Status</div>', unsafe_allow_html=True)
        gm = df.groupby(["Gender", "Married"])["Loan_Status"].apply(
            lambda s: round((s == "Y").sum() / len(s) * 100, 1)
        ).reset_index(name="Approval Rate (%)")
        gm["Segment"] = gm["Gender"] + " / " + gm["Married"].map({"Yes": "Married", "No": "Single"})
        fig6 = px.bar(gm, x="Segment", y="Approval Rate (%)", color="Segment",
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig6.update_layout(margin=dict(t=10, b=10), plot_bgcolor="white", showlegend=False)
        st.plotly_chart(fig6, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 2 — DATA MANAGEMENT
# ══════════════════════════════════════════════
elif page == "📁 Data Management":
    st.title("📁 Data Management")
    st.caption("Load, inspect, and clean your loan dataset.")

    uploaded = st.file_uploader("Upload a new CSV dataset", type=["csv"],
                                 help="Must include columns: Gender, Married, Dependents, Education, Self_Employed, "
                                      "ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, "
                                      "Credit_History, Property_Area, Loan_Status")

    try:
        raw_df, df = get_data(uploaded)
    except FileNotFoundError:
        st.error("Default dataset not found. Please upload a CSV file above.")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["📋 Raw Data", "🧹 Cleaned Data", "📈 Data Quality"])

    with tab1:
        st.markdown(f"**{len(raw_df):,} rows × {len(raw_df.columns)} columns**")
        st.dataframe(raw_df, use_container_width=True, height=420)

    with tab2:
        st.markdown(f"**{len(df):,} rows × {len(df.columns)} columns** after cleaning")
        st.dataframe(df, use_container_width=True, height=420)
        st.download_button(
            "⬇ Download Cleaned CSV",
            data=df.to_csv(index=False),
            file_name="loan_cleaned.csv",
            mime="text/csv",
        )

    with tab3:
        st.markdown('<div class="section-header">Missing Value Summary (Raw Dataset)</div>', unsafe_allow_html=True)
        missing = get_missing_summary(raw_df)
        if missing.empty:
            st.success("✅ No missing values detected in the dataset.")
        else:
            st.dataframe(missing, use_container_width=True)
            fig_m = px.bar(missing.reset_index(), x="index", y="Missing %",
                           labels={"index": "Column"}, color_discrete_sequence=["#e53935"])
            fig_m.update_layout(plot_bgcolor="white")
            st.plotly_chart(fig_m, use_container_width=True)

        st.markdown('<div class="section-header">Dataset Statistics</div>', unsafe_allow_html=True)
        st.dataframe(df.describe(include="all").T, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 3 — MACHINE LEARNING
# ══════════════════════════════════════════════
elif page == "🤖 Machine Learning":
    st.title("🤖 Machine Learning Models")
    st.caption("Train multiple classifiers, compare their performance, and auto-select the best model.")

    try:
        raw_df, df = get_data()
    except FileNotFoundError:
        st.warning("Dataset not found. Please upload one on the Data Management page.")
        st.stop()

    if "Loan_Status" not in df.columns:
        st.error("Dataset must contain a 'Loan_Status' column to train models.")
        st.stop()

    col_left, col_right = st.columns([1, 2])
    with col_left:
        test_size = st.slider("Test split ratio", 0.10, 0.40, 0.20, 0.05)
        train_btn = st.button("🚀 Train All Models", type="primary", use_container_width=True)

    # Show previously saved meta if available
    meta = load_model_meta()
    if meta and not train_btn:
        st.info(f"ℹ️ Showing results from last training session. Best model: **{meta['best_model_name']}**")

    if train_btn:
        with st.spinner("Training Logistic Regression, Decision Tree, and Random Forest…"):
            X, y, _, _ = prepare_features(df)
            results, best_name = train_and_evaluate(X, y, test_size=test_size)
            st.session_state["ml_results"] = results
            st.session_state["best_name"] = best_name
        st.success(f"✅ Training complete! Best model: **{best_name}**")
        meta = load_model_meta()

    # Display metrics table
    if meta:
        records = []
        for model_name, m in meta["metrics"].items():
            records.append({
                "Model": model_name,
                "Accuracy": f"{m['accuracy']:.2%}",
                "Precision": f"{m['precision']:.2%}",
                "Recall": f"{m['recall']:.2%}",
                "F1 Score": f"{m['f1']:.2%}",
                "Best": "⭐" if model_name == meta["best_model_name"] else "",
            })
        st.markdown('<div class="section-header">Model Comparison</div>', unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(records).set_index("Model"), use_container_width=True)

        # Bar chart comparison
        metric_df = pd.DataFrame([
            {
                "Model": n,
                "Accuracy": m["accuracy"],
                "Precision": m["precision"],
                "Recall": m["recall"],
                "F1 Score": m["f1"],
            }
            for n, m in meta["metrics"].items()
        ])
        fig_comp = px.bar(
            metric_df.melt(id_vars="Model", var_name="Metric", value_name="Score"),
            x="Metric", y="Score", color="Model", barmode="group",
            color_discrete_sequence=px.colors.qualitative.Bold,
            range_y=[0, 1],
        )
        fig_comp.update_layout(plot_bgcolor="white", yaxis_tickformat=".0%")
        st.plotly_chart(fig_comp, use_container_width=True)

        # Confusion matrices
        if "ml_results" in st.session_state:
            st.markdown('<div class="section-header">Confusion Matrices</div>', unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, (model_name, res) in enumerate(st.session_state["ml_results"].items()):
                cm = np.array(res["confusion_matrix"])
                fig_cm = px.imshow(
                    cm,
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=["Rejected", "Approved"], y=["Rejected", "Approved"],
                    text_auto=True, color_continuous_scale="Blues",
                    title=model_name,
                )
                fig_cm.update_layout(margin=dict(t=40, b=10))
                cols[idx % 3].plotly_chart(fig_cm, use_container_width=True)

        # Feature importances
        model = load_best_model()
        if model and meta:
            st.markdown('<div class="section-header">Feature Importances — Best Model</div>', unsafe_allow_html=True)
            imp_df = get_feature_importances(model, meta.get("feature_names", FEATURE_COLS))
            if imp_df is not None:
                fig_imp = px.bar(
                    imp_df, x="Importance", y="Feature", orientation="h",
                    color="Importance", color_continuous_scale="Blues",
                )
                fig_imp.update_layout(plot_bgcolor="white", yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig_imp, use_container_width=True)
    else:
        st.info("Click **Train All Models** to start.")


# ══════════════════════════════════════════════
# PAGE 4 — LOAN PREDICTION
# ══════════════════════════════════════════════
elif page == "💳 Loan Prediction":
    st.title("💳 Loan Prediction")
    st.caption("Enter applicant details to get an instant AI-powered loan approval decision.")

    model = load_best_model()
    meta = load_model_meta()
    if model is None:
        st.warning("⚠️ No trained model found. Please go to **Machine Learning** and train the models first.")
        st.stop()

    model_name = meta["best_model_name"] if meta else "Best Model"
    st.info(f"Using model: **{model_name}**")

    with st.form("prediction_form"):
        st.markdown('<div class="section-header">Applicant Information</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            gender = st.selectbox("Gender", ["Male", "Female"])
            married = st.selectbox("Marital Status", ["Yes", "No"])
            dependents = st.selectbox("Dependents", ["0", "1", "2", "3+"])
        with c2:
            education = st.selectbox("Education", ["Graduate", "Not Graduate"])
            self_employed = st.selectbox("Self Employed", ["No", "Yes"])
            property_area = st.selectbox("Property Area", ["Urban", "Semiurban", "Rural"])
        with c3:
            credit_history = st.selectbox("Credit History", [1, 0],
                                          format_func=lambda x: "Good (1)" if x == 1 else "None (0)")
            loan_amount_term = st.selectbox(
                "Loan Term (months)",
                [360, 180, 120, 240, 300, 480, 60, 36, 84],
                format_func=lambda x: f"{x} months ({x // 12} yrs)" if x >= 12 else f"{x} months",
            )

        st.markdown('<div class="section-header">Financial Details</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns(3)
        with f1:
            applicant_income = st.number_input("Applicant Monthly Income (₹)", min_value=0, value=5000, step=500)
        with f2:
            coapplicant_income = st.number_input("Co-applicant Monthly Income (₹)", min_value=0, value=0, step=500)
        with f3:
            loan_amount = st.number_input("Loan Amount (₹ thousands)", min_value=1, value=150, step=10)

        submitted = st.form_submit_button("🔍 Predict Loan Approval", type="primary", use_container_width=True)

    if submitted:
        applicant_data = {
            "Gender": gender,
            "Married": married,
            "Dependents": dependents,
            "Education": education,
            "Self_Employed": self_employed,
            "ApplicantIncome": applicant_income,
            "CoapplicantIncome": coapplicant_income,
            "LoanAmount": loan_amount,
            "Loan_Amount_Term": loan_amount_term,
            "Credit_History": credit_history,
            "Property_Area": property_area,
        }

        feature_vector = encode_single_input(applicant_data)
        prediction, probability, confidence = predict_loan(model, feature_vector)
        approved = prediction == "Approved"

        # Save to DB
        save_prediction(applicant_data, prediction, probability, model_name)

        # Result display
        st.markdown("---")
        res_col, gauge_col = st.columns([1, 1])

        with res_col:
            css_class = "result-approved" if approved else "result-rejected"
            icon = "✅" if approved else "❌"
            color = "#2e7d32" if approved else "#c62828"
            pct = round(probability * 100, 1)
            st.markdown(f"""
            <div class="{css_class}">
                <div class="result-title" style="color:{color}">{icon} Loan {prediction}</div>
                <div style="font-size:18px;color:#555">Approval Probability: <b style="color:{color}">{pct}%</b></div>
                <div style="margin-top:8px;font-size:14px;color:#666">Confidence: <b>{confidence}</b></div>
            </div>
            """, unsafe_allow_html=True)

        with gauge_col:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(probability * 100, 1),
                title={"text": "Approval Probability (%)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2e7d32" if approved else "#c62828"},
                    "steps": [
                        {"range": [0, 50],  "color": "#ffcdd2"},
                        {"range": [50, 70], "color": "#fff9c4"},
                        {"range": [70, 100],"color": "#c8e6c9"},
                    ],
                    "threshold": {"line": {"color": "black", "width": 3}, "thickness": 0.75, "value": 50},
                },
                number={"suffix": "%"},
            ))
            fig_gauge.update_layout(height=250, margin=dict(t=30, b=10, l=20, r=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        # Decision explanation
        st.markdown('<div class="section-header">Decision Explanation</div>', unsafe_allow_html=True)
        feature_names = meta.get("feature_names", list(applicant_data.keys())) if meta else list(applicant_data.keys())
        explanations = get_decision_explanation(feature_vector, feature_names, model)
        for exp in explanations:
            st.markdown(f"• {exp}")

        # Applicant summary
        with st.expander("📋 Submitted Applicant Details"):
            summary = pd.DataFrame([applicant_data]).T
            summary.columns = ["Value"]
            st.dataframe(summary, use_container_width=True)


# ══════════════════════════════════════════════
# PAGE 5 — PREDICTION HISTORY
# ══════════════════════════════════════════════
elif page == "📜 Prediction History":
    st.title("📜 Prediction History")
    st.caption("Review, search, and export all past loan predictions.")

    # Summary KPIs
    db_stats = get_summary_stats()
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{db_stats['total']:,}</div>
        <div class="kpi-label">Total Predictions</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card green"><div class="kpi-value">{db_stats['approved']:,}</div>
        <div class="kpi-label">Approved</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card red"><div class="kpi-value">{db_stats['rejected']:,}</div>
        <div class="kpi-label">Rejected</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Search & filter
    sc1, sc2, sc3 = st.columns([2, 1, 1])
    with sc1:
        search = st.text_input("🔍 Search predictions…", placeholder="gender, city, approved…")
    with sc2:
        filter_pred = st.selectbox("Filter by outcome", ["All", "Approved", "Rejected"])
    with sc3:
        filter_conf = st.selectbox("Filter by confidence", ["All", "High", "Medium", "Low"])

    df_hist = get_predictions(search)

    if filter_pred != "All":
        df_hist = df_hist[df_hist["prediction"] == filter_pred]
    if filter_conf != "All":
        df_hist = df_hist[df_hist["confidence"] == filter_conf]

    if df_hist.empty:
        st.info("No predictions recorded yet. Make a prediction on the **Loan Prediction** page.")
    else:
        # Colour-code the outcome column
        def highlight_prediction(row):
            if row["prediction"] == "Approved":
                return ["background-color: #e8f5e9"] * len(row)
            else:
                return ["background-color: #ffebee"] * len(row)

        display_cols = [
            "id", "timestamp", "gender", "married", "education",
            "property_area", "applicant_income", "loan_amount",
            "credit_history", "prediction", "probability", "confidence", "model_used",
        ]
        show_cols = [c for c in display_cols if c in df_hist.columns]
        styled = df_hist[show_cols].style.apply(highlight_prediction, axis=1)
        st.dataframe(styled, use_container_width=True, height=420)

        # Download
        csv_data = df_hist.to_csv(index=False)
        st.download_button(
            "⬇ Download History as CSV",
            data=csv_data,
            file_name="prediction_history.csv",
            mime="text/csv",
            type="primary",
        )

        # Mini analytics on history
        if len(df_hist) > 1:
            st.markdown('<div class="section-header">History Analytics</div>', unsafe_allow_html=True)
            hc1, hc2 = st.columns(2)

            with hc1:
                pie_data = df_hist["prediction"].value_counts().reset_index()
                pie_data.columns = ["Outcome", "Count"]
                fig_pie = px.pie(pie_data, names="Outcome", values="Count",
                                 color="Outcome",
                                 color_discrete_map={"Approved": "#2e7d32", "Rejected": "#c62828"})
                fig_pie.update_layout(margin=dict(t=20, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)

            with hc2:
                fig_prob = px.histogram(df_hist, x="probability", nbins=20,
                                        color_discrete_sequence=["#1565c0"],
                                        labels={"probability": "Approval Probability"},
                                        title="Probability Distribution")
                fig_prob.update_layout(plot_bgcolor="white", margin=dict(t=40, b=10))
                st.plotly_chart(fig_prob, use_container_width=True)
