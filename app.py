# app.py

import streamlit as st
import pdfplumber
from docx import Document
import re
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI-Powered Resume Analyzer",
    layout="wide"
)

st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #f5f7fa;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("AI-Powered Resume Analyzer")
st.caption("Upload a resume and instantly analyze candidate details, skills, and job fit.")

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "Upload resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

df = pd.DataFrame()

# ---------------- TEXT EXTRACTION ----------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

# ---------------- FIELD EXTRACTION ----------------
def extract_email(text):
    match = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match[0] if match else ""

def extract_phone(text):
    match = re.findall(r"\+?\d{10,13}", text)
    return match[0] if match else ""

def extract_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0].title() if lines else ""

def extract_education(text):
    keywords = ["B.Tech", "BE", "M.Tech", "ME", "MBA", "B.Sc", "M.Sc", "PhD"]
    return ", ".join([k for k in keywords if k.lower() in text.lower()])

technical_skills_list = [
    "Python", "Java", "C++", "SQL", "Machine Learning",
    "Deep Learning", "Data Analysis", "NLP", "Power BI", "Excel"
]

non_technical_skills_list = [
    "Communication", "Leadership", "Teamwork",
    "Problem Solving", "Time Management", "Creativity"
]

def extract_skills(text):
    found = [s for s in technical_skills_list + non_technical_skills_list if s.lower() in text.lower()]
    return found

def extract_certifications_projects(text):
    keywords = ["certified", "certification", "project", "internship"]
    return "; ".join([l.strip() for l in text.split("\n") if any(k in l.lower() for k in keywords)])

# ---------------- MAIN APP ----------------
if uploaded_file:
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = extract_text_from_docx(uploaded_file)

    st.markdown("### 📄 Resume Breakdown")

    tab1, tab2, tab3 = st.tabs(["🧑 Profile", "🛠 Skills", "📚 Education"])

    skills_found = extract_skills(resume_text)
    technical_skills = [s for s in skills_found if s in technical_skills_list]
    non_technical_skills = [s for s in skills_found if s in non_technical_skills_list]

    with tab1:
        st.write(resume_text[:900])

    with tab2:
        st.write("**Technical Skills:**", ", ".join(technical_skills))
        st.write("**Non-Technical Skills:**", ", ".join(non_technical_skills))

    with tab3:
        st.write(extract_education(resume_text))

    data = {
        "Name": extract_name(resume_text),
        "Email": extract_email(resume_text),
        "Phone": extract_phone(resume_text),
        "Education": extract_education(resume_text),
        "Technical Skills": ", ".join(technical_skills),
        "Non-Technical Skills": ", ".join(non_technical_skills),
        "Certifications & Projects": extract_certifications_projects(resume_text)
    }

    df = pd.DataFrame([data])

    st.markdown("### 📊 Resume Analysis Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Candidate Details")
        st.dataframe(df[["Name", "Email", "Phone", "Education"]], height=200)

    with col2:
        st.subheader("Skills Overview")
        st.dataframe(df[["Technical Skills", "Non-Technical Skills"]], height=200)

    st.markdown("### 🎯 Job Match Simulator")

    jd_skills = st.text_area(
        "Paste Job Description Skills (comma separated)",
        "Python, SQL, Communication, Data Analysis"
    )

    if jd_skills:
        jd_list = [s.strip().lower() for s in jd_skills.split(",")]
        resume_skill_list = [s.lower() for s in skills_found]

        match_count = len(set(jd_list) & set(resume_skill_list))
        match_percent = int((match_count / len(jd_list)) * 100)

        st.metric("Skill Match %", f"{match_percent}%")

        if match_percent >= 70:
            st.success("Strong match for the role")
        elif match_percent >= 40:
            st.warning("Partial match – consider upskilling")
        else:
            st.error("Low match – resume needs alignment")

    with st.expander("🔍 View Full Extracted Resume Text"):
        st.text_area("Resume Content", resume_text, height=300)

    st.markdown("### 📥 Export Data")
    csv = df.to_csv(index=False)
    st.download_button(
        "Download CSV",
        csv,
        "resume_analysis.csv",
        "text/csv"
    )
