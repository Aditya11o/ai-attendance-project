import html
import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout, style_student_portal

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
from src.pipelines.voice_pipeline import get_voice_embedding
from src.database.db import get_all_students, create_student, get_student_subjects, get_student_attendance, unenroll_student_to_subject
import time

from src.components.dialog_enroll import enroll_dialog
from src.components.icons import html_icon, st_icon
from src.components.subject_card import subject_card

def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        safe_name = html.escape(str(student_data['name']))
        st.markdown(f'<h3 class="student-subsection-heading">Welcome, {safe_name}</h3>', unsafe_allow_html=True)
        if st.button("Logout", type='secondary', key='loginbackbtn', icon=st_icon('logout'), shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data 
            st.rerun()


    st.space()

    c1, c2 =st.columns(2)
    with c1:
        st.markdown(f'<h2 class="student-section-heading">{html_icon("subjects", size="lg", extra_class="sc-heading-icon")}Your Enrolled Subjects</h2>', unsafe_allow_html=True)
    with c2:
        if st.button('Enroll in Subject', type='primary', icon=st_icon('add'), width='stretch'):
            enroll_dialog()


    st.divider()


    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total":0, "attended": 0}

        stats_map[sid]['total'] +=1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1


    cols = st.columns(2)
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']


        stats = stats_map.get(sid,{"total":0, "attended": 0} )
        def unenroll_button(subject_id=sid, subject_name=sub['name']):
                if st.button(
                    "Unenroll from this course",
                    key=f"unenroll_{subject_id}",
                    type='tertiary',
                    width='stretch',
                    icon=st_icon('unenroll'),
                ):
                    unenroll_student_to_subject(student_id, subject_id)
                    st.toast(f"Unenrolled from {subject_name} successfully!", icon=st_icon('attended'))
                    st.rerun()

        with cols[i % 2]:

            subject_card(
                name = sub['name'],
                code =sub['subject_code'],
                section = sub['section'],
                stats = [
                    ('total_classes', 'Total', stats['total']),
                    ('attended', 'Attended', stats['attended']),
                ],
                footer_callback=unenroll_button
            )
    footer_dashboard()


def student_screen():


    style_background_dashboard()
    style_base_layout()
    style_student_portal()

    with st.container(key="student_portal"):
        if "student_data" in st.session_state:
            student_dashboard()
            return
        
        c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
        with c1:
            header_dashboard()
        with c2:
            if st.button("Go back to Home", type='secondary', key='loginbackbtn', icon=st_icon('back'), shortcut="control+backspace"):
                st.session_state['login_type'] = None
                st.rerun()

        st.markdown(f'<h2 class="student-main-heading">{html_icon("face_id", size="lg", extra_class="sc-heading-icon")}Login using FaceID</h2>', unsafe_allow_html=True)
        st.space()
        st.space()
        
        show_registration = False
        photo_source = st.camera_input("Position your face in the center")

        if photo_source:
            img = np.array(Image.open(photo_source))

            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.warning('Face not found!', icon=st_icon('warning'))
                elif num_faces >1:
                    st.warning('Multiple faces found', icon=st_icon('warning'))
                else:
                    if detected:
                        student_id = list(detected.keys())[0]
                        all_students = get_all_students()
                        student = next((s for s in all_students if s['student_id']==student_id), None)

                        if student:
                            st.session_state.is_logged_in = True
                            st.session_state.user_role = 'student'
                            st.session_state.student_data = student
                            st.toast(f'Welcome Back {student['name']}', icon=st_icon('welcome'))
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info('Face not recognized! You might be a new student!', icon=st_icon('info'))
                        show_registration = True
        if show_registration:
            with st.container(border=True):
                st.markdown(f'<h2 class="student-section-heading">{html_icon("register", size="lg", extra_class="sc-heading-icon")}Register new Profile</h2>', unsafe_allow_html=True)
                new_name = st.text_input("Enter your name", placeholder='E.g. Hamza Rizvi')

                st.markdown(f'<h3 class="student-subsection-heading">{html_icon("mic", size="md", extra_class="sc-heading-icon")}Optional : Voice Enrollment</h3>', unsafe_allow_html=True)
                st.info("Enroll your for voice only attendance", icon=st_icon('info'))


                audio_data = None

                try:
                    audio_data = st.audio_input('Record a short phrase like I am present, My name is Akash.')
                except Exception:
                    st.error('Audio Data failed!', icon=st_icon('error'))

                if st.button('Create Account', type='primary', icon=st_icon('register')):
                    if new_name:
                        with st.spinner('Creating profile..'):
                            img = np.array(Image.open(photo_source))
                            encodings= get_face_embeddings(img)
                            if encodings:
                                face_emb = encodings[0].tolist()

                                voice_emb = None
                                if audio_data:
                                    voice_emb = get_voice_embedding(audio_data.read())

                                response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                                if response_data:
                                    train_classifier()
                                    st.session_state.is_logged_in = True
                                    st.session_state.user_role = 'student'
                                    st.session_state.student_data = response_data[0]
                                    st.toast(f'Profile Created! Hi {new_name}!', icon=st_icon('attended'))
                                    time.sleep(1)
                                    st.rerun()
                            else:
                                st.error('Couldnt capture your facial features for registration', icon=st_icon('error'))

                    else:
                        st.warning('Please enter your name!', icon=st_icon('warning'))


            
        footer_dashboard()