import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import io
from datetime import datetime

# -------------------------------------------------------
# 🔒 AUTHENTICATION SETUP
# -------------------------------------------------------
auth_config = st.secrets["auth"]

authenticator = stauth.Authenticate(
    auth_config["names"],
    auth_config["usernames"],
    auth_config["passwords"],
    auth_config["cookie_name"],
    auth_config["signature_key"],
    cookie_expiry_days=auth_config["cookie_expiry_days"]
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

    # -------------------------------------------------------
    # 🧾 SAMPLE DATA (replace with your actual source)
    # -------------------------------------------------------
    data = {
        "Date": pd.date_range(start="2025-01-01", periods=10, freq="D"),
        "Officer": ["Officer A", "Officer B"] * 5,
        "Inspected": [True, False] * 5,
        "Remarks": ["Good", "Needs Improvement"] * 5
    }
    df = pd.DataFrame(data)

    # -------------------------------------------------------
    # 📅 DATE RANGE FILTER
    # -------------------------------------------------------
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

    # -------------------------------------------------------
    # 💾 EXCEL DOWNLOAD SECTION
    # -------------------------------------------------------
    st.markdown("### 💾 Download Data (Excel)")

    def convert_df_to_excel(dataframe):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()

    excel_data = convert_df_to_excel(df)  # full dataset

    st.download_button(
        label="⬇️ Download Complete Dataset (Excel)",
        data=excel_data,
        file_name=f"goshala_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✅ Dashboard loaded successfully!")
