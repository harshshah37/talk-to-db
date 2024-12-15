import streamlit as st

def nav_bar():
    with st.sidebar:
        st.markdown(
        """
        <h2 style = "font-size: 24px; color: #4CAF50;">Navigation</h2>
        """,
        unsafe_allow_html=True)
        st.page_link('main.py', label = 'Home Page', icon = '🏠')
        st.page_link('pages/login.py', label = 'Login', icon = '🔑')
        st.page_link('pages/signup.py', label = 'Sign Up', icon = '📝')
        st.page_link('pages/query_page.py', label = 'Query Builder', icon = '✏️')