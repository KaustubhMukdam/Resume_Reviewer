import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Resume Reviewer Batch Dashboard")

df = pd.read_csv("outputs/batch_matrix.csv")
# Ensure all object columns are strings for display
for col in df.columns:
    if df[col].dtype == "object":
        df[col] = df[col].apply(lambda x: str(x))

st.subheader("Full Candidate-JD Matrix")
st.dataframe(df, width='stretch')

with st.sidebar:
    st.header("Filter Options")
    jd_selected = st.selectbox("Select JD", ["ALL"] + list(df["jd_filename"].unique()))
    candidate_selected = st.selectbox("Select Candidate", ["ALL"] + list(df["resume_filename"].unique()))
    score_choice = st.selectbox("Ranking Score", ["overall_score", "ats_composite_score"])
    top_n = st.slider("Top Candidates Number", 1, 10, 3)

filtered = df.copy()
if jd_selected != "ALL":
    filtered = filtered[filtered["jd_filename"] == jd_selected]
if candidate_selected != "ALL":
    filtered = filtered[filtered["resume_filename"] == candidate_selected]

st.subheader("Filtered Results")
st.dataframe(filtered, width='stretch')

st.markdown("---")
st.markdown("### Top Candidates per JD")

for jd in filtered["jd_filename"].unique():
    st.markdown(f"<h4><u>JD: {jd}</u></h4>", unsafe_allow_html=True)
    sub = filtered[filtered["jd_filename"] == jd]
    best = sub.sort_values(score_choice, ascending=False).head(top_n).copy()
    if "report_path" in best.columns:
        best["PDF Report"] = [
            f"[Download]({row['report_path']})" if isinstance(row["report_path"], str) and "pdf" in row["report_path"] else "" 
            for _, row in best.iterrows()
        ]
    display_cols = ["resume_filename", score_choice, "ats_composite_score", "matched_skills", "PDF Report"]
    display_cols = list(dict.fromkeys(display_cols))
    st.dataframe(
        best[display_cols],
        width='stretch'
    )

    # Format Suggestions Section
    if "resume_format_suggestions" in best.columns:
        for _, row in best.iterrows():
            st.markdown(f"<span style='color:#dc2626;font-weight:bold'>🛠️ Format Suggestions:</span>", unsafe_allow_html=True)
            suggs = row['resume_format_suggestions'].split("\\n") if "\\n" in row['resume_format_suggestions'] else row['resume_format_suggestions'].split("\n")
            for sugg in suggs:
                st.markdown(f"<div style='margin-left: 20px; color:#2563eb;'>• {sugg.strip()}</div>", unsafe_allow_html=True)

    # Interview Questions Section
    if "interview_questions" in best.columns:
        for _, row in best.iterrows():
            st.write("")
            with st.expander(f"Interview Questions for {row['resume_filename']}", expanded=False):
                questions = row["interview_questions"].split("\\n") if "\\n" in row["interview_questions"] else row["interview_questions"].split("\n")
                for q in questions:
                    q_clean = q.replace("**", "")  # Remove extra markdown bold
                    st.markdown(f"<div style='margin-left: 20px;'>• {q_clean.strip()}</div>", unsafe_allow_html=True)
            st.markdown("---")
    st.markdown("---")
