import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import io
from datetime import datetime

# --- Authentication Setup ---
# Define user credentials (you can move this to .streamlit/secrets.toml for security)
names = ["Admin", "Viewer"]
usernames = ["admin", "viewer"]
passwords = ["admin123", "view123"]

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

# --- Handle Authentication States ---
if auth_status is False:
    st.error("❌ Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your username and password to continue.")
else:
    # --- Main Dashboard Content ---
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")

    st.title("📊 Goshala Inspection Dashboard")
    st.write("Access granted — you are now viewing the full dashboard.")

    # Example data loading (replace with your Google Sheet or local data)
    data = {
        "Date": pd.date_range(start="2025-01-01", periods=10, freq="D"),
        "Officer": ["Officer A", "Officer B"] * 5,
        "Inspected": [True, False] * 5,
        "Remarks": ["Good", "Needs Improvement"] * 5
    }

    df = pd.DataFrame(data)

    # --- Date Range Filter ---
    st.markdown("---")
    st.subheader("📅 Filter by Date Range")

    min_date = df["Date"].min()
    max_date = df["Date"].max()

    start_date, end_date = st.date_input(
        "Select date range:", [min_date, max_date], min_value=min_date, max_value=max_date
    )

    filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]

    st.dataframe(filtered_df)

    # --- Excel Download Button ---
    st.markdown("### 💾 Download Data (Excel)")

    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()

    excel_data = convert_df_to_excel(df)

    st.download_button(
        label="⬇️ Download Full Dataset (Excel)",
        data=excel_data,
        file_name=f"goshala_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
