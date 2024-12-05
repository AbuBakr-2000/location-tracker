import streamlit as st
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Login", layout="wide")

# Check if already logged in and session not expired
if st.session_state.get("authenticated") and \
   st.session_state.get("login_time") and \
   datetime.now() - st.session_state["login_time"] < timedelta(hours=3):
    st.switch_page("app.py")

# Admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Center the login form
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("🔐 Login")
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state["authenticated"] = True
                st.session_state["login_time"] = datetime.now()
                st.success("Login successful!")
                st.switch_page("app.py")
            else:
                st.error("Invalid username or password")
