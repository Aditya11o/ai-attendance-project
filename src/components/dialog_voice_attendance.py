from datetime import datetime

import pandas as pd
import streamlit as st

from src.components.dialog_attendance_results import show_attendance_result
from src.components.icons import st_icon
from src.database.config import supabase
from src.pipelines.voice_pipeline import process_bulk_audio


@st.dialog('Voice Attendance')
def voice_attendance_dialog(selected_subject_id):
    st.write(
        'Record audio of students saying "Present" or "I am present". '
        'AI detects positive attendance intent and matches the enrolled speaker.'
    )

    if st.session_state.get('voice_attendance_subject_id') != selected_subject_id:
        st.session_state.voice_attendance_results = None
        st.session_state.voice_attendance_meta = None
        st.session_state.voice_attendance_subject_id = selected_subject_id

    audio_data = st.audio_input("Record classroom audio")

    if st.button(
        'Analyze Audio',
        width='stretch',
        type='primary',
        icon=st_icon('mic'),
        disabled=audio_data is None,
    ):
        if audio_data is None:
            st.warning('Please record classroom audio before analyzing.', icon=st_icon('warning'))
            return

        audio_bytes = (
            audio_data.getvalue()
            if hasattr(audio_data, 'getvalue')
            else audio_data.read()
        )
        if not audio_bytes:
            st.warning('Recorded audio is empty. Please record again.', icon=st_icon('warning'))
            return

        with st.spinner('Processing audio data...'):
            enrolled_res = (
                supabase.table('subject_students')
                .select("*, students(*)")
                .eq('subject_id', selected_subject_id)
                .execute()
            )
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No students enrolled in this course', icon=st_icon('warning'))
                return

            candidates_dict = {
                s['students']['student_id']: s['students']['voice_embedding']
                for s in enrolled_students
                if s['students'].get('voice_embedding')
            }

            if not candidates_dict:
                st.error('No enrolled students have voice profiles registered', icon=st_icon('error'))
                return

            analysis = process_bulk_audio(audio_bytes, candidates_dict, return_details=True)
            identified = analysis.get('identified', {})
            unidentified = analysis.get('unidentified_segments', [])
            rejected = analysis.get('rejected_segments', [])

            results, attendance_to_log = [], []
            current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                match_info = identified.get(student['student_id'])
                is_present = bool(match_info)
                speaker_score = float(match_info['speaker_score']) if match_info else 0.0

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Source": f"{speaker_score:.2f}" if is_present else "-",
                    "Status": "Present" if is_present else "Absent",
                })

                attendance_to_log.append({
                    'student_id': student['student_id'],
                    'subject_id': selected_subject_id,
                    'timestamp': current_timestamp,
                    'is_present': bool(is_present),
                })

            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)
            st.session_state.voice_attendance_meta = {
                'unidentified': unidentified,
                'rejected': rejected,
            }

    if st.session_state.get('voice_attendance_results'):
        st.divider()
        base_df, base_logs = st.session_state.voice_attendance_results
        meta = st.session_state.get('voice_attendance_meta') or {}
        unidentified = meta.get('unidentified', [])
        rejected = meta.get('rejected', [])

        review_df = base_df.copy()
        review_logs = [dict(row) for row in base_logs]

        if unidentified:
            segment_notes = ", ".join(
                f'"{seg["transcript"]}" ({seg["start_sec"]:.1f}s-{seg["end_sec"]:.1f}s, '
                f'best voice={seg["best_speaker_score"]:.2f})'
                for seg in unidentified
            )
            st.warning(
                f'Requires teacher review: Detected positive "Present" speech from an '
                f'unidentified speaker ({segment_notes}). No student was auto-marked.',
                icon=st_icon('warning'),
            )
            absent_options = {
                f"{row['Name']} (ID: {row['ID']})": row['ID']
                for _, row in review_df.iterrows()
                if row['Status'] == 'Absent'
            }
            if absent_options:
                selected_labels = st.multiselect(
                    'Manual teacher review override (optional: mark Present)',
                    options=list(absent_options.keys()),
                    key=f'voice_review_override_{selected_subject_id}',
                )
                selected_ids = {absent_options[lbl] for lbl in selected_labels}
                if selected_ids:
                    mask = review_df['ID'].isin(selected_ids)
                    review_df.loc[mask, 'Source'] = 'Teacher Review'
                    review_df.loc[mask, 'Status'] = 'Present'
                    for entry in review_logs:
                        if entry['student_id'] in selected_ids:
                            entry['is_present'] = True

        if rejected:
            ignored_notes = ", ".join(
                f'"{seg["transcript"]}" ({seg["intent"]})'
                for seg in rejected
            )
            st.info(
                f'Ignored non-confirming audio segments: {ignored_notes}',
                icon=st_icon('info'),
            )

        show_attendance_result(review_df, review_logs)
