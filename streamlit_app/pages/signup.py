import streamlit as st
from shared import auth, db, hash_password
from modules.nav import Navbar

def signup(navigate_to):

    Navbar()

    st.title("Sign Up")
    st.subheader("Create a New Account")

    with st.form("signup_form"):
        email = st.text_input("Email", placeholder = "Enter your email")
        password = st.text_input("Password", placeholder = "Enter your password", type = "password")
        confirm_password = st.text_input("Confirm Password", placeholder = "Re-enter your password", type = "password")
        submit_button = st.form_submit_button("Sign Up")

    if submit_button:

        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not email or not password:
            st.error("Email and Password fields cannot be empty!")
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                st.success("Account created successfully!")

                hashed_password = hash_password(password)
                user_data = {"email": email, "password": hashed_password}
                id_token = user["idToken"]
                db.child("users").push(user_data, id_token)

                st.session_state.page = "login"
                st.rerun() 
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button("Back to Main", key = "back_to_main"):
        navigate_to("main")
