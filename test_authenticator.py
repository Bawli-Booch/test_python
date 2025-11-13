import streamlit as st
import streamlit_authenticator as stauth

st.title("✅ Streamlit Authenticator Fixed Example")

auth = st.secrets["auth"]

names = list(auth["names"])
usernames = list(auth["usernames"])
passwords = list(auth["passwords"])
cookie_name = str(auth["cookie_name"])
signature_key = str(auth["signature_key"])
cookie_expiry_days = int(auth["cookie_expiry_days"])

# ✅ FIX: cookie_expiry_days passed positionally, not as keyword
authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    cookie_name,
    signature_key,
    cookie_expiry_days
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status is False:
    st.error("❌ Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your username and password.")
else:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")
    st.success(f"✅ Logged in as {username}")
