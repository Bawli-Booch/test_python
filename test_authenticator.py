import streamlit as st
import streamlit_authenticator as stauth
import traceback

st.title("🔍 Streamlit Authentication Debug Tool")

# ------------------------------------------------------------
# STEP 1️⃣  Test: Can Streamlit see secrets.toml at all?
# ------------------------------------------------------------
st.subheader("Step 1️⃣ – Secrets visibility check")

try:
    st.write("🔹 Full secrets dictionary:")
    st.json(st.secrets)  # shows everything Streamlit can see
except Exception as e:
    st.error(f"❌ Could not access secrets: {e}")
    st.stop()

# ------------------------------------------------------------
# STEP 2️⃣  Check for 'auth' key
# ------------------------------------------------------------
st.subheader("Step 2️⃣ – Check for [auth] section")

if "auth" not in st.secrets:
    st.error("❌ No [auth] section found in secrets.toml! "
             "Please create `.streamlit/secrets.toml` with [auth] header, "
             "or add the same content under 'Manage App → Secrets' in Streamlit Cloud.")
    st.stop()
else:
    st.success("✅ [auth] section found.")
    auth_config = st.secrets["auth"]
    st.json(auth_config)

# ------------------------------------------------------------
# STEP 3️⃣  Verify required keys exist
# ------------------------------------------------------------
st.subheader("Step 3️⃣ – Verify all keys exist")

required_keys = ["names", "usernames", "passwords", "cookie_name", "signature_key", "cookie_expiry_days"]
missing = [k for k in required_keys if k not in auth_config]

if missing:
    st.error(f"❌ Missing keys in [auth]: {missing}")
    st.stop()
else:
    st.success("✅ All required keys are present.")

# ------------------------------------------------------------
# STEP 4️⃣  Safely load values with type checks
# ------------------------------------------------------------
st.subheader("Step 4️⃣ – Convert and verify data types")

try:
    names = list(auth_config["names"])
    usernames = list(auth_config["usernames"])
    passwords = list(auth_config["passwords"])
    cookie_name = str(auth_config["cookie_name"])
    signature_key = str(auth_config["signature_key"])
    cookie_expiry_days = int(auth_config["cookie_expiry_days"])

    st.write("✅ Data types look good:")
    st.write(f"- names: {type(names)} ({len(names)} entries)")
    st.write(f"- usernames: {type(usernames)} ({len(usernames)} entries)")
    st.write(f"- passwords: {type(passwords)} ({len(passwords)} entries)")
    st.write(f"- cookie_name: {cookie_name}")
    st.write(f"- signature_key: {signature_key[:5]}********")
    st.write(f"- cookie_expiry_days: {cookie_expiry_days}")

except Exception as e:
    st.error(f"❌ Error converting secrets data: {e}")
    st.exception(e)
    st.stop()

# ------------------------------------------------------------
# STEP 5️⃣  Test authenticator creation
# ------------------------------------------------------------
st.subheader("Step 5️⃣ – Initialize streamlit-authenticator")

try:
    authenticator = stauth.Authenticate(
        names,
        usernames,
        passwords,
        cookie_name,
        signature_key,
        cookie_expiry_days=cookie_expiry_days
    )
    st.success("✅ Authenticator object created successfully.")
except Exception as e:
    st.error("❌ Error creating authenticator:")
    st.exception(e)
    st.stop()

# ------------------------------------------------------------
# STEP 6️⃣  Test login UI
# ------------------------------------------------------------
st.subheader("Step 6️⃣ – Test login UI")

try:
    name, auth_status, username = authenticator.login("Login", "main")

    if auth_status is False:
        st.error("❌ Invalid username or password.")
    elif auth_status is None:
        st.info("🟡 Please enter credentials above.")
    else:
        authenticator.logout("Logout", "sidebar")
        st.sidebar.success(f"Welcome, {name}")
        st.success(f"✅ Login successful as: {name} ({username})")

except Exception as e:
    st.error("❌ Exception in login process:")
    st.exception(e)
    st.stop()

# ------------------------------------------------------------
# STEP 7️⃣  Final confirmation
# ------------------------------------------------------------
st.markdown("---")
st.subheader("✅ Summary")

st.write("""
- If all steps above are green ✅, your secrets.toml and authenticator are configured correctly.  
- If you get a ❌ in Step 1 or 2 → the app can't read secrets (wrong path or missing section).  
- If Step 5 fails → check package version (`streamlit-authenticator==0.3.1`).  
""")
