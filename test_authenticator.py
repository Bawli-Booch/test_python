import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import io
from datetime import datetime

# --- Load credentials securely from secrets.toml ---
auth_config = st.secrets["auth"]

authenticator = stauth.Authenticate(
    auth_config["credentials"]["names"],
    auth_config["credentials"]["usernames"],
    auth_config["credentials"]["passwords"],
    auth_config["cookie_name"],
    auth_config["signature_key"],
    cookie_expiry_days=auth_config["cookie_expiry_days"]
)

name, auth_status, username = authenticator.login("Login", "main")

# --- Authentication flow ---
if auth_status is False:
    st.error("❌ Invalid username or password")
elif auth_status is None:
    st.warning("Please enter your username and password to continue.")
else:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome, {name}")

    st.title("📊 Goshala Inspection Dashboard")
    st.write("✅ You are successfully logged in and can now view all dashboard data.")

    # Example dataset
    data = {
        "Date": pd.date_range(start="2025-01-01", periods=10, freq="D"),
        "Officer": ["Officer A", "Officer B"] * 5,
        "Inspected": [True, False] * 5,
        "Remarks": ["Good", "Needs Improvement"] * 5
    }
    df = pd.DataFrame(data)

    # --- Date filter ---
    st.subheader("📅 Filter by Date Range")
    min_date, max_date = df["Date"].min(), df["Date"].max()
    start_date, end_date = st.date_input("Select date range:", [min_date, max_date])

    filtered_df = df[
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    st.dataframe(filtered_df)

    # --- Excel download ---
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()

    st.download_button(
        "⬇️ Download Full Dataset (Excel)",
        convert_df_to_excel(df),
        file_name=f"goshala_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
