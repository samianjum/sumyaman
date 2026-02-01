from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/login/{user_type}/{user_id}/{dob}")
def login(user_type: str, user_id: str, dob: str):
    conn = sqlite3.connect('/home/sami/sumyaman/db.sqlite3')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if user_type == "Teacher":
        q = "SELECT *, assigned_class as cls, assigned_section as sec, 'Teacher' as role FROM apsokara_teacher WHERE cnic = ? AND dob = ?"
    else:
        q = "SELECT *, student_class as cls, student_section as sec, 'Student' as role FROM apsokara_student WHERE b_form = ? AND dob = ?"
    cursor.execute(q, (user_id, dob))
    row = cursor.fetchone()
    conn.close()
    return {"success": True, "data": dict(row)} if row else {"success": False}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
