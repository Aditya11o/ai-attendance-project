import streamlit as st
from src.components.icons import st_icon
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


from src.database.db import create_attendance


def _style_status_cell(val: str) -> str:
    """Apply semantic text color for attendance status values in review tables."""
    if val == "Present":
        return "color: #16A34A; font-weight: 600;"
    if val == "Absent":
        return "color: #EF4444; font-weight: 600;"
    return ""


def show_attendance_result(df, logs):
    st.write('Please review attendance before confirming.')
    display_data = (
        df.style.map(_style_status_cell, subset=['Status'])
        if not df.empty and 'Status' in df.columns
        else df
    )
    st.dataframe(display_data, hide_index=True, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        if st.button('Discard', icon=st_icon('close'), width='stretch'):
            st.session_state.voice_attendance_results = None
            st.session_state.voice_attendance_meta = None
            st.session_state.attendance_images = []
            st.rerun()

    with col2:
        if st.button('Confirm & Save', width='stretch', type='primary', icon=st_icon('done')):
            try:
                inserted = create_attendance(logs)
                if inserted:
                    st.toast("Attendance taken", icon=st_icon('attended'))
                else:
                    st.toast("Attendance already saved for this session", icon=st_icon('info'))
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.session_state.voice_attendance_meta = None
                st.rerun()
            except Exception as e:
                st.error('Sync failed!', icon=st_icon('error'))



@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)


