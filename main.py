import streamlit as st

st.set_page_config(
    page_title = "NL Query Builder",
    page_icon = "✏️",
    layout = "wide"
)

from pages.login import login
from pages.signup import signup
from pages.query_page import query_page
from modules.nav import nav_bar

def navigate_to(page):
    st.session_state.page = page 
    st.rerun()  

if "page" not in st.session_state:
    st.session_state.page = "main" 

if st.session_state.page == "main":

    nav_bar()

    st.markdown(
        """
        <div style="background-color:#4CAF50;padding:10px;border-radius:8px;">
            <h1 style="color:white;text-align:center;">Welcome to the App</h1>
        </div>
        """,
        unsafe_allow_html = True
    )

    st.markdown(
        """
        <h3 style="text-align:center;color:#333;">Your gateway to streamlined query generation and management</h3>
        <hr style="border-top: 2px solid #4CAF50;">
        """,
        unsafe_allow_html = True
    )

    col1, col2, col3 = st.columns([1, 1, 1]) 
    with col2:
        col_login, col_signup = st.columns([1, 1])  
        with col_login:
            if st.button("🔑 Login", key = "login_button"):
                navigate_to("login")
        with col_signup:
            if st.button("📝 Sign Up", key = "signup_button"):
                navigate_to("signup")

    st.markdown(
        """
        <hr>
        <p style="text-align:center;color:gray;font-size:14px;">Designed for simplicity and efficiency</p>
        """,
        unsafe_allow_html = True
    )

elif st.session_state.page == "login":
    login(navigate_to) 
elif st.session_state.page == "signup":
    signup(navigate_to) 
elif st.session_state.page == "query_page":
    query_page(navigate_to)  