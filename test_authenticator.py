import streamlit as st
import streamlit_authenticator as stauth

st.title("✅ Streamlit Authenticator – Final Fixed (v0.4.1+)")

# --- Read from secrets ---
auth = st.secrets["auth"]

cookie_name = str(auth["cookie_name"])
signature_key = str(auth["signature_key"])
cookie_expiry_days = int(auth["cookie_expiry_days"])

# --- Build credentials dict dynamically ---
credentials = {
    "usernames": {
        auth["usernames"][0]: {
            "name": auth["names"][0],
            "password": auth["passwords"][0]
        },
        auth["usernames"][1]: {
            "name": auth["names"][1],
            "password": auth["passwords"][1]
        }
    }
}

# --- Initialize authenticator (new API) ---
authenticator = stauth.Authenticate(
    credentials,
    cookie_name,
    signature_key,
    cookie_expiry_days
)

# ✅ New login syntax (v0.4.1 and newer)
name, auth_status, username = authenticator.login(fields={'Form name': 'Login'})

# --- Handle login state ---
if auth_status is False:
    st.error("❌ Invalid username or password.")
elif auth_status is None:
    st.info("🟡 Please enter your credentials to access the dashboard.")
else:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")
    st.success(f"✅ Logged in as {username}")
