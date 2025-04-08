import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

print("\n--- 📄 Resumes ---")
for row in cursor.execute("SELECT id, filename, email FROM resumes"):
    print(f"ID: {row[0]}, File: {row[1]}, Email: {row[2]}")

print("\n--- 📝 Job Descriptions ---")
for row in cursor.execute("SELECT id, title, description FROM job_descriptions"):
    print(f"\nID: {row[0]}")
    print(f"Title: {row[1]}")
    print(f"Description: {row[2][:500]}...")  # shows first 500 chars, remove [:500] to see full


count = cursor.execute("SELECT COUNT(*) FROM shortlisted").fetchone()[0]
print(f"\n🧠 Total Shortlisted Records: {count}")



print("\n--- 🎯 Shortlisted Matches ---")
query = '''
SELECT 
    s.id,
    r.filename,
    j.title,
    s.match_score
FROM shortlisted s
JOIN resumes r ON s.resume_id = r.id
JOIN job_descriptions j ON s.job_id = j.id
ORDER BY s.match_score DESC
'''

results = cursor.execute(query).fetchall()

if results:
    for row in results:
        print(f"\nShortlist ID: {row[0]}")
        print(f"Resume: {row[1]}")
        print(f"Job Title: {row[2]}")
        print(f"Match Score: {row[3]}%")
else:
    print("No shortlisted matches found.")

conn.close()
