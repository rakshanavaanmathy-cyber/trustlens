
import json
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="TrustLens",
    page_icon="🛡️",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@500;600;700&display=swap');

.stApp {
    background: radial-gradient(circle at top left, #183047, #080d18 48%);
    color: #edf5ff;
    font-family: 'DM Sans', sans-serif;
}
[data-testid="stSidebar"] {
    background: #0b1220;
    border-right: 1px solid #263850;
}
.block-container {
    max-width: 1450px;
    padding-top: 2rem;
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
}
.hero {
    background: linear-gradient(120deg, #182d4a, #10504d);
    padding: 32px;
    border-radius: 22px;
    border: 1px solid #31566a;
    margin-bottom: 24px;
}
.hero h1 {
    color: white;
    font-size: 42px;
}
.hero p {
    color: #d1e4ef;
    font-size: 16px;
}
.kpi {
    background: linear-gradient(145deg, #142136, #0e1727);
    border: 1px solid #293d56;
    border-radius: 16px;
    padding: 20px;
    min-height: 120px;
}
.kpi-label {
    color: #9bb0c8;
    font-size: 14px;
}
.kpi-value {
    color: #63e6c5;
    font-size: 32px;
    font-weight: 700;
    margin-top: 10px;
}
.panel {
    background: #101a2b;
    border: 1px solid #293b53;
    padding: 20px;
    border-radius: 16px;
}
.stButton button, .stDownloadButton button {
    border-radius: 10px;
    font-weight: 700;
}
.stTabs [data-baseweb="tab"] {
    background: #101a2b;
    border-radius: 8px;
}
hr {
    border-color: #293b53;
}
</style>
""", unsafe_allow_html=True)


# ---------- SAMPLE DATA ----------
def load_demo_data():
    return pd.DataFrame({
        "Order_ID": [
            1001, 1002, 1003, 1004, 1005, 1006,
            1007, 1007, 1009, 1010, 1011, 1012
        ],
        "Date": [
            "2026-10-01", "2026-10-01", "2026-10-02",
            "2026-10-02", "2026-10-03", "2026-10-03",
            "2026-10-04", "2026-10-04", "2026-10-05",
            "2026-10-05", "not-a-date", "2026-10-06"
        ],
        "Region": [
            "Chennai", "Coimbatore", "Chennai", "Madurai",
            "Trichy", "Chennai", "Salem", "Salem",
            "Coimbatore", None, "Madurai", "Chennai"
        ],
        "Sales": [
            12500, 8400, 9200, 15400, 6700, None,
            11900, 11900, -500, 7200, 6600, 13800
        ],
        "Units": [5, 3, 4, 7, 2, 4, 6, 6, 1, 3, 2, 5]
    })


# ---------- DATA ANALYSIS ----------
def analyse_data(df):
    total_cells = max(df.shape[0] * df.shape[1], 1)

    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    numeric = df.select_dtypes(include="number")

    negative = {
        col: int((numeric[col] < 0).sum())
        for col in numeric.columns
        if (numeric[col] < 0).any()
    }

    invalid_dates = {}

    for col in df.columns:
        if any(word in col.lower()
               for word in ["date", "time", "timestamp"]):
            parsed = pd.to_datetime(df[col], errors="coerce")
            invalid = parsed.isna() & df[col].notna()
            count = int(invalid.sum())

            if count:
                invalid_dates[col] = count

    empty_columns = [
        col for col in df.columns if df[col].isna().all()
    ]

    penalties = {
        "Missing values": min(40, missing / total_cells * 100),
        "Duplicate rows": min(
            25, duplicates / max(len(df), 1) * 100
        ),
        "Negative numbers": min(
            15, sum(negative.values()) / max(len(df), 1) * 100
        ),
        "Invalid dates": min(
            15, sum(invalid_dates.values()) / max(len(df), 1) * 100
        ),
        "Empty columns": min(10, len(empty_columns) * 5)
    }

    score = max(0, round(100 - sum(penalties.values())))

    issues = []

    if missing:
        issues.append({
            "Priority": "Medium",
            "Issue": "Missing values",
            "Count": missing,
            "Details": f"{missing} empty cells detected.",
            "Action": "Check the source data before filling missing values."
        })

    if duplicates:
        issues.append({
            "Priority": "High",
            "Issue": "Duplicate rows",
            "Count": duplicates,
            "Details": f"{duplicates} duplicate rows detected.",
            "Action": "Verify duplicate transactions before removing them."
        })

    if negative:
        issues.append({
            "Priority": "Medium",
            "Issue": "Negative numbers",
            "Count": sum(negative.values()),
            "Details": ", ".join(
                f"{col}: {count}"
                for col, count in negative.items()
            ),
            "Action": "Check business rules. Negative values may be valid."
        })

    if invalid_dates:
        issues.append({
            "Priority": "High",
            "Issue": "Invalid dates",
            "Count": sum(invalid_dates.values()),
            "Details": ", ".join(
                f"{col}: {count}"
                for col, count in invalid_dates.items()
            ),
            "Action": "Correct invalid date values before reporting."
        })

    if empty_columns:
        issues.append({
            "Priority": "High",
            "Issue": "Empty columns",
            "Count": len(empty_columns),
            "Details": ", ".join(empty_columns),
            "Action": "Check the source feed or remove unused columns."
        })

    return {
        "score": score,
        "missing": missing,
        "duplicates": duplicates,
        "negative": negative,
        "invalid_dates": invalid_dates,
        "empty_columns": empty_columns,
        "penalties": penalties,
        "issues": issues
    }


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("🛡️ TrustLens")
    st.caption("DATA RELIABILITY WORKSPACE")
    st.divider()

    source = st.radio(
        "Choose data source",
        ["Demo dataset", "Upload CSV"]
    )

    uploaded_file = None

    if source == "Upload CSV":
        uploaded_file = st.file_uploader(
            "Upload your CSV file",
            type=["csv"]
        )

    st.divider()
    st.caption("Checks: missing values, duplicates, invalid dates, negative numbers and empty columns.")


# ---------- LOAD DATA ----------
if source == "Upload CSV":
    if uploaded_file is None:
        st.markdown("""
        <div class="hero">
            <h1>TrustLens</h1>
            <p>Understand your data quality before trusting your dashboard.</p>
        </div>
        """, unsafe_allow_html=True)

        st.info("Upload a CSV file from the sidebar to start scanning.")
        st.stop()

    try:
        df = pd.read_csv(uploaded_file)
        filename = uploaded_file.name
    except Exception as error:
        st.error(f"Could not read the CSV: {error}")
        st.stop()

else:
    df = load_demo_data()
    filename = "Demo sales data"

if df.empty or len(df.columns) == 0:
    st.error("The dataset is empty.")
    st.stop()


# ---------- DASHBOARD ----------
results = analyse_data(df)
score = results["score"]

if score >= 90:
    status = "Healthy"
    emoji = "🟢"
elif score >= 70:
    status = "Needs attention"
    emoji = "🟡"
else:
    status = "At risk"
    emoji = "🔴"

st.markdown(f"""
<div class="hero">
    <p>DATA QUALITY INTELLIGENCE</p>
    <h1>Your data deserves to be trusted.</h1>
    <p>Detect data-quality problems, understand potential risks,
    and discover what needs investigation.</p>
    <p>● SCAN COMPLETE &nbsp; | &nbsp; {filename}</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Workspace overview")

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("Trust score", f"{score}/100"),
    ("Rows scanned", f"{len(df):,}"),
    ("Findings", str(len(results["issues"]))),
    ("Missing cells", str(results["missing"]))
]

for col, (label, value) in zip([c1, c2, c3, c4], cards):
    col.markdown(
        f'<div class="kpi">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.write("")

left, right = st.columns(2)

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader(f"{emoji} Trust health: {status}")
    st.progress(score / 100)
    st.write(f"**Quality score: {score}/100**")
    st.caption(
        "This is a rule-based screening score, not a guarantee "
        "that all business data is correct."
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.subheader("Scan details")
    st.write(f"**Source:** {filename}")
    st.write(f"**Rows:** {len(df):,}")
    st.write(f"**Columns:** {len(df.columns)}")
    st.write(f"**Scanned:** {datetime.now():%d %b %Y, %I:%M %p}")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Insights",
    "⚠️ Findings & actions",
    "🔎 Data explorer",
    "📥 Export report"
])


# ---------- INSIGHTS ----------
with tab1:
    chart_col, profile_col = st.columns(2)

    with chart_col:
        st.subheader("Missing values by column")

        missing_df = pd.DataFrame({
            "Column": df.columns,
            "Missing": df.isna().sum().values
        })

        fig = px.bar(
            missing_df,
            x="Column",
            y="Missing",
            color="Missing",
            color_continuous_scale=["#53e0c0", "#fbbf24", "#fb7185"],
            template="plotly_dark"
        )

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(fig, use_container_width=True)

    with profile_col:
        st.subheader("Dataset profile")

        profile = pd.DataFrame({
            "Column": df.columns,
            "Type": [str(df[col].dtype) for col in df.columns],
            "Unique values": [
                int(df[col].nunique(dropna=True))
                for col in df.columns
            ],
            "Missing": [
                int(df[col].isna().sum())
                for col in df.columns
            ]
        })

        st.dataframe(
            profile,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Trust score breakdown")

        penalty_df = pd.DataFrame({
            "Check": list(results["penalties"].keys()),
            "Penalty": list(results["penalties"].values())
        })

        penalty_fig = px.bar(
            penalty_df,
            x="Penalty",
            y="Check",
            orientation="h",
            template="plotly_dark"
        )

        penalty_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )

        st.plotly_chart(
            penalty_fig,
            use_container_width=True
        )


# ---------- FINDINGS ----------
with tab2:
    st.subheader("Detected issues and recommendations")

    if not results["issues"]:
        st.success("No issues detected by the current checks.")

    for issue in results["issues"]:
        with st.container(border=True):
            st.markdown(
                f"### {issue['Issue']} — {issue['Priority']}"
            )
            st.write(issue["Details"])
            st.write(f"**Count:** {issue['Count']}")
            st.info(f"Recommended action: {issue['Action']}")

    st.divider()
    st.subheader("Review checklist")

    st.checkbox("Confirm findings with the data owner")
    st.checkbox("Validate business rules before changing data")
    st.checkbox("Run the scan again after corrections")


# ---------- DATA EXPLORER ----------
with tab3:
    st.subheader("Explore your data")

    search_text = st.text_input(
        "Search across all columns",
        placeholder="Type a region, ID, date, or value..."
    )

    view = df.copy()

    if search_text.strip():
        mask = view.astype(str).apply(
            lambda column: column.str.contains(
                search_text,
                case=False,
                na=False,
                regex=False
            )
        )
        view = view[mask.any(axis=1)]

    st.caption(f"{len(view):,} matching rows")

    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download source CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="trustlens_data.csv",
        mime="text/csv"
    )


# ---------- EXPORT REPORT ----------
with tab4:
    st.subheader("Export TrustLens report")

    report = {
        "product": "TrustLens",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": filename,
        "trust_score": score,
        "status": status,
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": results["missing"],
        "duplicate_rows": results["duplicates"],
        "negative_values": results["negative"],
        "invalid_dates": results["invalid_dates"],
        "empty_columns": results["empty_columns"],
        "issues": results["issues"],
        "note": "Rule-based screening score. Review findings in business context."
    }

    report_json = json.dumps(report, indent=2)

    st.write(
        "Download a JSON report containing the score, findings, "
        "and recommended actions."
    )

    st.download_button(
        "⬇️ Download JSON report",
        data=report_json,
        file_name="trustlens_report.json",
        mime="application/json",
        type="primary"
    )

    with st.expander("Preview report"):
        st.code(report_json, language="json")


st.divider()
st.caption(
    "TRUSTLENS  |  Data quality intelligence for clearer decisions."
)
