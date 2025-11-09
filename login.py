import streamlit as st
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Login - Wildlife Conservation", page_icon="🌿", layout="centered")

# --- Page styling ---
st.markdown("""
    <style>
    .main-title { font-size: 2.4rem; color:#2E7D32; text-align:center; padding:1rem; }
    .stButton>button { background-color:#388E3C; color:white; border-radius:6px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🌿 Wildlife Conservation Management System</h1>", unsafe_allow_html=True)
st.markdown("### 🔐 Please Log In")

# --- Verify database credentials ---
def test_connection(user, password):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user=user,
            password=password,
            database="wildlife_conservation"
        )
        conn.close()
        return True
    except Error:
        return False

# --- Login form ---
with st.form("login_form"):
    username = st.selectbox(
        "Select User",
        ["app_user", "app_employee", "app_supervisor", "tanisha","bhoomika","root"]
    )
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

if submitted:
    if test_connection(username, password):
        st.session_state.user = username
        st.session_state.password = password

        # Role classification
        if username in ["app_user", "tanisha","bhoomika"]:
            st.session_state.role = "Viewer"
        elif username == "app_employee":
            st.session_state.role = "Employee"
        elif username in ["app_supervisor", "root"]:
            st.session_state.role = "Supervisor"
        else:
            st.session_state.role = "Unknown"

        st.success(f"✅ Logged in as {st.session_state.role}")
        st.switch_page("pages/appp.py")

    else:
        st.error("❌ Invalid credentials or unable to connect.")
