import streamlit as st


def _render_footer(text_color: str) -> None:
    """Render the centered application footer with the specified text color."""
    st.markdown(
        f"""
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center;">
            <p style="font-weight:bold; color:{text_color};">Created with ❤️ by Group A</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def footer_home():
    _render_footer("white")


def footer_dashboard():
    _render_footer("black")
