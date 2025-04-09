RecruitGeniusAI 🤖📄
RecruitGeniusAI is an AI-powered recruitment assistant that automates resume parsing, job description summarization, and candidate shortlisting using on-prem LLMs via Ollama. Built with a multi-agent design, it streamlines the hiring workflow—from uploading resumes and JDs to sending interview invites—all through a simple Streamlit frontend.

🚀 Features
Upload and parse resumes (PDF)

Summarize job descriptions from CSV

Match resumes with jobs using TinyLlama

Shortlist candidates based on match score (80%+)

Send personalized interview invites

SQLite database for data storage

Modular multi-agent backend

🛠 Tech Stack
Python, Streamlit, SQLite

LangChain, Ollama (TinyLlama)

PyPDF2, pandas, re (regex)

📂 Folder Structure
python
Copy
Edit
📁 RecruitGeniusAI/
├── 📄 backend.py          # Resume & JD parsing, matching logic
├── 📄 frontend.py         # Streamlit frontend UI
├── 📄 email_utils.py      # Email sending functions
├── 📄 match.py            # Prompt building & score extraction
├── 📂 resumes/            # PDF resumes folder
├── 📄 job_descriptions.csv # Job description dataset
├── 📄 database.db         # SQLite database
📌 How to Run
Clone the repo

Place PDF resumes in /resumes and fill job_descriptions.csv

Run frontend.py with streamlit run frontend.py
