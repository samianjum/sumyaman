import streamlit as st
import pandas as pd
from apsokara.models import Student

def show_student_manager():
    st.subheader("👨‍🎓 Student Database (Secure View)")
    
    # Privacy Toggle
    privacy_on = st.toggle("🔒 Privacy Mode (Mask Sensitive Data)", value=True)
    
    # Search
    search = st.text_input("🔍 Search Student (Name/Roll No)")
    
    if search:
        qs = Student.objects.filter(full_name__icontains=search) | \
             Student.objects.filter(roll_number__icontains=search)
    else:
        qs = Student.objects.all().order_by('-id')[:20]

    if qs.exists():
        data = []
        for s in qs:
            # Privacy Logic: Data ko chupa dena agar toggle on ho
            phone = "XXXX-XXXXXXX" if privacy_on else s.parents_phone
            b_form = "XXXXX-XXXXXXX-X" if privacy_on else s.b_form
            
            data.append({
                "ID": s.id,
                "Full Name": s.full_name,
                "Roll No": s.roll_number,
                "Class": s.student_class,
                "B-Form": b_form,
                "Parent Phone": phone
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if privacy_on:
            st.warning("⚠️ Sensitive data is hidden. Turn off 'Privacy Mode' to see full details.")
            
        st.divider()
        # Admin Action Area
        with st.expander("🛠️ Advanced Actions (Delete/Edit)"):
            target_id = st.number_input("Enter Student ID", min_value=0, step=1)
            if st.button("🗑️ Permanent Delete", type="primary"):
                try:
                    Student.objects.get(id=target_id).delete()
                    st.success(f"ID {target_id} deleted successfully!")
                    st.rerun()
                except:
                    st.error("Student ID not found!")
    else:
        st.info("No students found in the database.")

if __name__ == "__main__":
    pass
