from urllib.parse import quote
import io

import segno
import streamlit as st

from src.components.icons import html_icon, st_icon

DEFAULT_APP_URL = "https://snapclass-360.streamlit.app"


def build_join_url(subject_code: str, base_url: str = DEFAULT_APP_URL) -> str:
    """Build a full HTTPS join URL with an encoded join-code query parameter."""
    normalized_base = base_url.rstrip("/")
    encoded_code = quote(str(subject_code).strip(), safe="")
    return f"{normalized_base}/?join-code={encoded_code}"


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    join_url = build_join_url(subject_code)

    st.header("Scan to Join")

    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f'### {html_icon("link", size="md", extra_class="sc-heading-icon")}Copy Link', unsafe_allow_html=True)
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info('Copy this link to share on Whatsapp or Email', icon=st_icon('info'))

    with col2:
        st.markdown(f'### {html_icon("qr_code", size="md", extra_class="sc-heading-icon")}Scan to Join', unsafe_allow_html=True)
        st.image(out.getvalue(), caption='QRCODE for class joining')

        
