import os
import sqlite3
import pandas as pd
from PyPDF2 import PdfReader
import re
from match import extract_score, build_prompt
from langchain_ollama.llms import OllamaLLM

# ---------- CONFIG ----------
RESUME_FOLDER = 'resumes'
JD_CSV = 'job_descriptions.csv'
DB_NAME = 'database.db'
llm = OllamaLLM(model="tinyllama") 

# ---------- DATABASE SETUP ----------
def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shortlisted (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                job_id INTEGER,
                match_score REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                content TEXT,
                email TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT
            )
        ''')
        conn.commit()

# ---------- PARSE RESUMES ----------
def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        return " ".join([page.extract_text() or "" for page in reader.pages])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def extract_email(text):
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return emails[0] if emails else None

def save_resumes():
    uploaded = 0
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        for filename in os.listdir(RESUME_FOLDER):
            if filename.endswith(".pdf"):
                # Skip if resume already exists
                cursor.execute("SELECT id FROM resumes WHERE filename = ?", (filename,))
                if cursor.fetchone():
                    continue

                full_path = os.path.join(RESUME_FOLDER, filename)
                content = extract_text_from_pdf(full_path)
                email = extract_email(content)
                cursor.execute("INSERT INTO resumes (filename, content, email) VALUES (?, ?, ?)",
                               (filename, content, email))
                uploaded += 1

        conn.commit()
    
    return uploaded

# ---------- PARSE JOB DESCRIPTIONS ----------
def save_job_descriptions():
    uploaded = 0
    try:
        df = pd.read_csv(JD_CSV, encoding='ISO-8859-1')
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                title = str(row.get("Job Title", "Untitled"))
                description = str(row.get("Job Description", ""))
                # Avoid duplicates
                cursor.execute("SELECT id FROM job_descriptions WHERE title = ? AND description = ?", (title, description))
                if cursor.fetchone():
                    continue
                cursor.execute("INSERT INTO job_descriptions (title, description) VALUES (?, ?)", (title, description))
                uploaded += 1
            conn.commit()
    except Exception as e:
        print(f"Error reading CSV: {e}")
    
    return uploaded

# ---------- MATCHING AND SHORTLISTING ----------
def match_and_shortlist():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        resumes = cursor.execute("SELECT id, content FROM resumes").fetchall()
        jobs = cursor.execute("SELECT id, description FROM job_descriptions").fetchall()

        for resume_id, resume_text in resumes:
            for job_id, job_desc in jobs:
                prompt = build_prompt(resume_text, job_desc)
                response = llm.invoke(prompt)
                score = extract_score(response)

                if score is not None and score >= 80:
                    cursor.execute(
                        "INSERT INTO shortlisted (resume_id, job_id, match_score) VALUES (?, ?, ?)",
                        (resume_id, job_id, score)
                    )
                    count = cursor.execute("SELECT COUNT(*) FROM shortlisted").fetchone()[0]
                    print(f"\n📊 Total shortlisted entries: {count}")
                    print(f"✅ Matched resume {resume_id} with job {job_id}: {score}%")

        conn.commit()

# ---------- MAIN ----------
if __name__ == "__main__":
    initialize_database()
    save_resumes()
    save_job_descriptions()
    match_and_shortlist()
    print("✅ All operations completed successfully.")
