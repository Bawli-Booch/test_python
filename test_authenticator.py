import streamlit as st
import streamlit_authenticator as stauth

names = ["Admin", "Viewer"]
usernames = ["admin", "viewer"]
passwords = ["admin123", "view123"]

# Generate hashed passwords
hashed_pw = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names,
    usernames,
    hashed_pw,
    "goshala_dashboard_cookie",
    "auth_signature_key",
    cookie_expiry_days=1
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("❌ Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your username and password to continue.")
else:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")
    st.title("Secure Dashboard Example")
