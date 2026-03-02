file_path = '/home/sami/sumyaman/main_app.py'

with open(file_path, 'r') as f:
    content = f.read()

# 1. SQL Queries ko correct models ke mutabiq set karein
import re
content = re.sub(r'q = "SELECT \* FROM apsokara_teacher WHERE .*"', 'q = "SELECT * FROM apsokara_teacher WHERE cnic = ? AND dob = ?"', content)
content = re.sub(r'q = "SELECT \* FROM apsokara_student WHERE .*"', 'q = "SELECT * FROM apsokara_student WHERE b_form = ? AND dob = ?"', content)

# 2. Teacher Table ke columns ko Streamlit variables se match karein
# Teacher table mein 'assigned_wing' hai, code mein 'wing' dhoond raha hai
content = content.replace("st.session_state.user_data['wing']", "st.session_state.user_data['assigned_wing'] if 'assigned_wing' in st.session_state.user_data else st.session_state.user_data.get('wing', 'None')")

# 3. Agar data fetch karte waqt direct index use ho raha hai to usay sambhalein
content = content.replace("user_data['wing']", "user_data['assigned_wing'] if 'assigned_wing' in user_data else user_data.get('wing', 'None')")

with open(file_path, 'w') as f:
    f.write(content)

print("✅ main_app.py updated for Teacher (assigned_wing) and Student (wing)!")
