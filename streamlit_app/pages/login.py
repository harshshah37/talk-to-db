import streamlit as st
from shared import auth
from modules.nav import Navbar

def login(navigate_to):

    Navbar()

    st.title("Login")
    st.subheader("Access Your Account")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder = "Enter your email")
        password = st.text_input("Password", placeholder = "Enter your password", type = "password")
        submit_button = st.form_submit_button("Log In")

    if submit_button:
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success(f"Welcome back, {email}!")

            st.session_state.page = "query_page"
            st.rerun()  
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("Back to Main", key = "back_to_main"):
        navigate_to("main")
