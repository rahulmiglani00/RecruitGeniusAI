
def build_prompt(resume_text, job_description):
    return f"""
You are an AI assistant helping with recruitment.

Given the resume content and a job description, compare them and provide a match score out of 100%. Just give the score in the format: "Match Score: XX%".

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{job_description}
\"\"\"

Please output only: Match Score: XX%
"""

import re

def extract_score(response_text):
    match = re.search(r"Match Score[:\-]?\s*(\d{1,3})%", response_text)
    return float(match.group(1)) if match else None

