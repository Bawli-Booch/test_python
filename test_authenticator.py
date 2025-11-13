import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import io
from datetime import datetime

# -------------------------------------------------------
# 🔒 AUTHENTICATION SETUP
# -------------------------------------------------------
auth_config = st.secrets["auth"]

names = list(auth_config["names"])
usernames = list(auth_config["usernames"])
passwords = list(auth_config["passwords"])
cookie_name = str(auth_config["cookie_name"])
signature_key = str(auth_config["signature_key"])
cookie_expiry_days = int(auth_config["cookie_expiry_days"])

authenticator = stauth.Authenticate(
    names,
    usernames,
    passwords,
    cookie_name,
    signature_key,
    cookie_expiry_days=cookie_expiry_days
)

name, auth_status, username = authenticator.login("Login", "main")

# -------------------------------------------------------
# 🚧 AUTHENTICATION STATES
# -------------------------------------------------------
if auth_status is False:
    st.error("❌ Invalid username or password. Please try again.")
elif auth_status is None:
    st.warning("👋 Please enter your username and password to access the dashboard.")
else:
    # -------------------------------------------------------
    # ✅ MAIN DASHBOARD CONTENT
    # -------------------------------------------------------
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")

    st.title("📊 Goshala Inspection Dashboard")
    st.write("You are now logged in and can view the complete dashboard.")

    # Example dataset
    data = {
        "Date": pd.date_range(start="2025-01-01", periods=10, freq="D"),
        "Officer": ["Officer A", "Officer B"] * 5,
        "Inspected": [True, False] * 5,
        "Remarks": ["Good", "Needs Improvement"] * 5
    }
    df = pd.DataFrame(data)

    # Date Range Filter
    st.markdown("---")
    st.subheader("📅 Filter by Date Range")

    min_date, max_date = df["Date"].min(), df["Date"].max()
    start_date, end_date = st.date_input(
        "Select date range:",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    st.dataframe(filtered_df)

    # Excel Download
    st.markdown("### 💾 Download Data (Excel)")

    def convert_df_to_excel(dataframe):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()

    excel_data = convert_df_to_excel(df)

    st.download_button(
        label="⬇️ Download Complete Dataset (Excel)",
        data=excel_data,
        file_name=f"goshala_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✅ Dashboard loaded successfully!")
