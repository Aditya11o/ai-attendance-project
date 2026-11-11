import html as html_lib
import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    safe_name = html_lib.escape(str(name))
    safe_code = html_lib.escape(str(code))
    safe_section = html_lib.escape(str(section))

    html = f"""
        <div class="subject-card" style="background:white; border-left: 8px solid #EB459E; padding:25px; border-radius: 20px; border: 1px solid black; margin-bottom:20px;">
        <h3 style="margin:0; color: #1e293b; font-size: 1.5rem ">{safe_name}</h3>
        <p style="color:#64748b; margin:10px 0;">Code : <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:5px;">{safe_code} </span> | Section : {safe_section}</p>
        
        """
    
    if stats:
        html+= """
        <div class="subject-card-stats" style="display:flex; gap:8px; flex-wrap:wrap;">
        """
        for icon, label, value in stats:
            safe_label = html_lib.escape(str(label))
            safe_value = html_lib.escape(str(value))
            html+= f'<div class="subject-card-stat-badge" style="background: #EB459E10; padding:5px 12px; border-radius:12px; font-size:0.9rem">{icon} <b class="subject-card-stat-value">{safe_value}</b> {safe_label} </div>'
        
        html+= "</div>"

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()
