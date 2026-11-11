import streamlit as st
from src.components.icons import st_icon
from src.database.db import create_subject



@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")


    if st.button("Create Subject Now", type='primary', icon=st_icon('add'), width='stretch'):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Succesfully!", icon=st_icon('attended'))
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}", icon=st_icon('error'))
        else:
            st.warning("Please fill all the fields", icon=st_icon('warning'))
