import streamlit as st



def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #5865F2 !important;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:#E0E3FF !important;
                    padding:2.5rem !important;
                    border-radius: 5rem !important;
                    }

                .stApp div[data-testid="stColumn"] h2.portal-card-heading {
                    font-family: 'Climate Crisis', sans-serif !important;
                    font-size: clamp(1.35rem, 2.2vw, 1.85rem) !important;
                    line-height: 1.25 !important;
                    color: #1E293B !important;
                    background: transparent !important;
                    text-shadow: none !important;
                    text-align: left !important;
                    margin: 0 0 0.75rem 0 !important;
                    padding: 0 !important;
                    letter-spacing: 0.01em !important;
                    overflow-wrap: break-word !important;
                }

                .stApp div[data-testid="stColumn"] h2.portal-card-heading::selection {
                    background-color: rgba(88, 101, 242, 0.22) !important;
                    color: #1E293B !important;
                }

                @media (max-width: 768px) {
                    .stApp div[data-testid="stColumn"] h2.portal-card-heading {
                        font-size: 1.4rem !important;
                        line-height: 1.25 !important;
                    }
                }
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #E0E3FF !important;
                }

        </style>  

                """
            ,unsafe_allow_html=True)


def _style_portal_scope(
    scope_key: str,
    prefix: str,
    extra_rules: str = "",
    include_generic_headings: bool = True,
) -> None:
    """Apply scoped typography and high-contrast colors for a portal container."""
    generic_heading_rules = ""
    if include_generic_headings:
        generic_heading_rules = f"""
            .st-key-{scope_key} [data-testid="stHeadingWithActionElements"] h2 {{
                color: #202B3F !important;
                line-height: 1.25 !important;
            }}

            .st-key-{scope_key} [data-testid="stHeadingWithActionElements"] h3 {{
                color: #202B3F !important;
                line-height: 1.35 !important;
            }}
        """

    st.markdown(f"""
        <style>
            .st-key-{scope_key} h2.{prefix}-main-heading {{
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: clamp(1.45rem, 3vw, 2.1rem) !important;
                line-height: 1.25 !important;
                color: #202B3F !important;
                text-align: center !important;
                margin: 0.25rem 0 1.25rem 0 !important;
                padding: 0 !important;
                background: transparent !important;
                overflow-wrap: break-word !important;
            }}

            .st-key-{scope_key} h2.{prefix}-section-heading {{
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: clamp(1.3rem, 2.4vw, 1.8rem) !important;
                line-height: 1.25 !important;
                color: #202B3F !important;
                text-align: left !important;
                margin: 0 0 0.75rem 0 !important;
                padding: 0 !important;
                background: transparent !important;
                overflow-wrap: break-word !important;
            }}

            .st-key-{scope_key} h3.{prefix}-subsection-heading {{
                font-family: 'Outfit', sans-serif !important;
                font-size: clamp(1.05rem, 2vw, 1.3rem) !important;
                font-weight: 700 !important;
                line-height: 1.35 !important;
                color: #202B3F !important;
                margin: 0.75rem 0 0.5rem 0 !important;
                padding: 0 !important;
                background: transparent !important;
            }}
            {generic_heading_rules}

            .st-key-{scope_key} [data-testid="stWidgetLabel"],
            .st-key-{scope_key} [data-testid="stWidgetLabel"] label,
            .st-key-{scope_key} [data-testid="stWidgetLabel"] p,
            .st-key-{scope_key} [data-testid="stWidgetLabel"] span {{
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.95rem !important;
                font-weight: 600 !important;
                line-height: 1.45 !important;
                color: #30343B !important;
            }}

            .st-key-{scope_key} [data-testid="stAudioInput"] [data-testid="stWidgetLabel"],
            .st-key-{scope_key} [data-testid="stAudioInput"] [data-testid="stWidgetLabel"] p,
            .st-key-{scope_key} [data-testid="stSpinner"] p,
            .st-key-{scope_key} [data-testid="stCaptionContainer"],
            .st-key-{scope_key} [data-testid="stImageCaption"] {{
                font-family: 'Outfit', sans-serif !important;
                font-size: 0.95rem !important;
                font-weight: 500 !important;
                line-height: 1.45 !important;
                color: #4B5563 !important;
            }}

            .st-key-{scope_key} [data-testid="stMarkdownContainer"] div[style*="EB459E10"] {{
                color: #30343B !important;
            }}
            {extra_rules}

            @media (max-width: 768px) {{
                .st-key-{scope_key} h2.{prefix}-main-heading {{
                    font-size: 1.45rem !important;
                    margin-bottom: 1rem !important;
                }}

                .st-key-{scope_key} h2.{prefix}-section-heading {{
                    font-size: 1.3rem !important;
                }}

                .st-key-{scope_key} [data-testid="stWidgetLabel"],
                .st-key-{scope_key} [data-testid="stWidgetLabel"] p {{
                    font-size: 0.9rem !important;
                }}
            }}
        </style>
        """, unsafe_allow_html=True)


def style_student_portal():
    """Apply scoped typography and high-contrast colors for the Student Portal."""
    _style_portal_scope("student_portal", "student")


def style_teacher_portal():
    """Apply scoped typography and high-contrast colors for the Teacher Portal."""
    teacher_badge_rules = """
            .st-key-teacher_portal .subject-card .subject-card-stat-badge {
                color: #30343B !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 500 !important;
                line-height: 1.35 !important;
            }

            .st-key-teacher_portal .subject-card .subject-card-stat-badge b.subject-card-stat-value {
                color: #202B3F !important;
                font-weight: 700 !important;
            }
    """
    _style_portal_scope(
        "teacher_portal",
        "teacher",
        extra_rules=teacher_badge_rules,
        include_generic_headings=False,
    )
    

    

def style_base_layout():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

                
         /* Hide Top Bar of streamlit */
                
            #MainMenu, footer, header {
                visibility: hidden;
            }
                
            .block-container {
                padding-top:1.5rem !important;    
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height: 1.1 !important;
                margin-bottom:0rem !important;
            }
                

            h2 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 2rem !important;
                line-height: 1.2 !important;
                margin-bottom:0rem !important;
            }
                
            h3, h4, p {
                font-family: 'Outfit', sans-serif;    
            }
                

            button{
                border-radius: 1.5rem !important;
                background-color: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="secondary"]{
                border-radius: 1.5rem !important;
                background-color: #EB459E !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button[kind="tertiary"]{
                border-radius: 1.5rem !important;
                background-color: black !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

            button:hover{
                transform :scale(1.05)}
        </style>  

                """
            ,unsafe_allow_html=True)