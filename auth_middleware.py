import os
import hmac
import pickle
import streamlit as st
from pathlib import Path

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Get admin password from environment variable
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin")
    
    # Check if user is already authenticated
    if st.session_state.get("authenticated"):
        return True
    
    # Create login fields
    st.markdown("## 🔐 Authentication Required")
    st.markdown("Please enter your credentials to access this application.")
    username = st.text_input("Username", value="admin", disabled=True)
    password = st.text_input("Password", type="password")
    
    # Check if password is correct
    if st.button("Login"):
        if username == "admin" and password == admin_password:
            st.session_state["authenticated"] = True
            return True
        else:
            st.error("Invalid password. Please try again.")
            return False
    
    return False

def auth_required(func):
    """Decorator to require authentication for a Streamlit app function."""
    def wrapper(*args, **kwargs):
        if check_password():
            # If authentication is successful, redirect back to the main page
            # to clear the password input and URL parameters
            if "authenticated" in st.session_state and st.session_state["authenticated"]:
                func(*args, **kwargs)
        # If not authenticated, the check_password function already shows the login form
    return wrapper

# Initialize session state variables if they don't exist
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False