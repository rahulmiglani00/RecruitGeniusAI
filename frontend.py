import streamlit as st
import sqlite3
import pandas as pd
import os
from backend import save_resumes, save_job_descriptions, match_and_shortlist, initialize_database
from email_utils import send_email


# ---------- CONFIG ----------
DB_NAME = 'database.db'
initialize_database()

# ---------- STREAMLIT UI ----------
st.set_page_config(page_title="RecruitGeniusAI", layout="wide")
st.title("🤖 RecruitGeniusAI")

tab1, tab2, tab3 = st.tabs(["📄 Upload Data", "📊 Match Candidates", "✅ Shortlisted Candidates"])

# ---------- UPLOAD RESUMES & JOBS ----------
with tab1:
    if st.button("Upload Resumes"):
        uploaded = save_resumes()
        if uploaded:
            st.success(f"✅ {uploaded} new resume(s) uploaded successfully!")
        else:
            st.warning("⚠️ No new resumes were uploaded.")

    if st.button("Upload Job Descriptions"):
        uploaded = save_job_descriptions()
        if uploaded:
            st.success(f"✅ {uploaded} new job description(s) uploaded successfully!")
        else:
            st.warning("⚠️ No new job descriptions were uploaded.")

# ---------- MATCH & SHORTLIST ----------
with tab2:
    if st.button("🚀 Match and Shortlist Candidates"):
        match_and_shortlist()
        st.success("✅ Matching & shortlisting complete!")

# ---------- VIEW SHORTLISTED ----------
with tab3:
    st.subheader("📝 Shortlisted Candidates")

    conn = sqlite3.connect(DB_NAME)
    query = '''
        SELECT s.id, r.filename AS resume_file, r.email, j.title AS job_title, s.match_score, s.resume_id, s.job_id
        FROM shortlisted s
        JOIN resumes r ON s.resume_id = r.id
        JOIN job_descriptions j ON s.job_id = j.id
    '''
    df_shortlisted = pd.read_sql_query(query, conn)

    if df_shortlisted.empty:
        st.info("No shortlisted candidates yet.")
    else:
        # Display table
        display_df = df_shortlisted[["resume_file", "email", "job_title", "match_score"]]
        display_df.columns = ["Resume", "Email", "Job Title", "Match Score"]
        st.dataframe(display_df, use_container_width=True)

        st.subheader("📧 Send Emails")

        def get_email_by_resume_id(resume_id):
            cur = conn.cursor()
            cur.execute("SELECT email FROM resumes WHERE id = ?", (resume_id,))
            result = cur.fetchone()
            return result[0] if result else None

        def email_body_template(job_id):
            cur = conn.cursor()
            cur.execute("SELECT title FROM job_descriptions WHERE id = ?", (job_id,))
            result = cur.fetchone()
            title = result[0] if result else "a job opportunity"
            return f"""Hello,

You have been shortlisted for {title} based on your resume.

Please reply to this email to schedule your interview.

Best regards,
RecruitGeniusAI Team
"""

        for i, row in df_shortlisted.iterrows():
            resume_id = row["resume_id"]
            job_id = row["job_id"]
            match_score = row["match_score"]
            email = row["email"]

            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📨 **Email**: {email} | 💼 Job: {row['job_title']} | ✅ Score: {match_score}%")
            with col2:
                if st.button(f"Send Email to {email}", key=f"email_{i}"):
                    body = email_body_template(job_id)
                    sent = send_email(email, "You're Shortlisted!", body)
                    if sent:
                        st.success(f"✅ Email sent to {email}")
                    else:
                        st.error(f"❌ Failed to send email to {email}")

        if st.button("📢 Send Email to All"):
            for i, row in df_shortlisted.iterrows():
                email = row["email"]
                body = email_body_template(row["job_id"])
                send_email(email, "You're Shortlisted!", body)
            st.success("✅ Emails sent to all shortlisted candidates.")

    conn.close()
