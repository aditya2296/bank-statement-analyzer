import streamlit as st

def login():
    st.title("🔐Account Statement Analyzer")

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")

    if login_btn:
        # Replace this check with your authentication logic
        if username == "admin" and password == "pass123":
            st.session_state.authenticated = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password")