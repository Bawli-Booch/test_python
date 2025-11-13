import streamlit as st
import streamlit_authenticator as stauth


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
    # --- Top right logout button ---
    col1, col2 = st.columns([8, 2])
    with col2:
        authenticator.logout("🔓 Logout", "main")
    with col1:
        st.success(f"Welcome, {name}")

    # step1_app.py
    # Goshala Inspection Dashboard - Full version
    # Light theme, tabs (no sidebar), interactive map, PDF generator for all tabs
    # Uses Google Sheet ID: 1WZ1mKLGvUj24lLvjzP0CwF8_IBIK4jSqxPikTtiSLVg
    
    import streamlit as st
    import pandas as pd
    import numpy as np
    import altair as alt
    import plotly.express as px
    import plotly.graph_objects as go
    from fpdf import FPDF
    from io import BytesIO
    from datetime import datetime, date
    import base64
    import math
    import warnings
    warnings.filterwarnings("ignore")
    
    st.set_page_config(page_title="Goshala Inspection Dashboard", layout="wide")
    
    # -------------------------------
    # CONFIG / PATHS / CONSTANTS
    # -------------------------------
    GSHEET_ID = "1WZ1mKLGvUj24lLvjzP0CwF8_IBIK4jSqxPikTtiSLVg"
    # CSV export URL for first sheet. If you need a specific sheet tab, set GID below.
    GSHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/export?format=csv"
    
    LOCAL_STATIC_PATH = "goshala_static_data.xlsx"  # adjust if uploaded elsewhere
    
    # Date-named PDF filename helper
    def pdf_filename():
        return f"goshala_dashboard_summary_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # -------------------------------
    # COLUMN RENAME MAPPING (from provided mapping)
    # -------------------------------
    COL_RENAME = {
        "Created At": "created_at",
        "निरीक्षण अधिकारी प्रकार": "inspector_type",
        "निरीक्षण अधिकारी का पद चुनें": "inspector_designation",
        "अधिकारी का नाम": "officer_name",
        "निरीक्षण अधिकारी का नंबर": "officer_mobile",
        "निरीक्षण का प्रकार": "inspection_type",
        "गांव / गोवंश आश्रय स्थल का प्रकार": "shelter_category",
        "विकास खंड/ नगर निकाय": "block_name_static",
        "गोवंश संरक्षण स्थल का नाम": "shelter_name_static",
        "गांव / गोवंश आश्रय स्थल का नाम": "village_name_static",
        "गोवंश संरक्षित की क्षमता": "shelter_capacity_static",
        "संरक्षित गोंवंश": "protected_cattle_static",
        "ईअर टेगिंग की संख्या": "ear_tag_count_static",
        "बधियाकरण": "castration_count_static",
        "मृत पशुओं की संख्या": "dead_animals_count_static",
        "कृत्रिम गर्भाधान": "artificial_insemination_count_static",
        "सुपर्दगी गोवंश": "handover_cattle_static",
        "लाभार्थियों की संख्या": "beneficiary_count_static",
        "GPS Location": "gps_location_static",
        "गोशाला का प्रकार": "goshala_type",
        "उपलब्ध गोंवंश की संख्या": "available_cattle",
        "उपलब्ध शेड की संख्या": "shed_count",
        "शेड में उपलब्ध पंखों की संख्या": "fan_count",
        "बोर से ढके शेड की संख्या": "roofed_shed_count",
        "शेड के ऊपर पानी के छिड़काव की स्थिति": "shed_spray_status",
        "शेड में वेंटिलेशन की स्थिति": "ventilation_status",
        "उपलब्ध शेड में साफ़ सफ़ाई की व्यवस्था?": "cleanliness_arrangement",
        "शेड की फोटो डालें": "shed_photo",
        "उपलब्ध सभी शेड का कुल क्षेत्रफल ( वर्ग फीट)": "total_shed_area_sqft",
        "गोशाला की अधिकतम क्षमता": "max_capacity",
        "उपलब्ध शेड मौजूद पशुओं के लिए प्रयापत है?": "shed_adequate_animals_1",
        "उपलब्ध शेड मौजूद पशुओं के लिए प्रयापत है? ": "shed_adequate_animals_2",
        "अपर्याप्त शेड की दशा में अतिरिक्त शेड के निर्माण की स्थिति": "additional_shed_status",
        "अतिरिक्त शेड निर्माण की वर्तमान स्थिति": "additional_shed_current_status",
        "कुल ईअर टेगिंग किए हुए पशुओं की संख्या": "total_eartagged_cattle",
        "ताजा पेयजल की व्यवस्था": "drinking_water",
        "गोशाला पर मौजूद पानी भंडारण की क्षमता ( लीटर में)": "water_storage_capacity_litre",
        "पानी का स्रोत्र की फोटो": "water_source_photo",
        "उपलब्ध भूसा गोदाम की संख्या": "fodder_godown_count",
        "उपलब्ध अस्थाई खोप की संख्या": "temp_shed_count",
        "उपलब्ध भूसे की मात्रा ( क्विंटल में)": "fodder_quantity_quintal",
        "उपलब्ध भूसा कितने दिन के लिए प्रयापत है?": "fodder_days_available",
        "भूसे की फोटो": "fodder_photo",
        "उपलब्ध चोकर - आहार की मात्रा (KG)": "bran_feed_quantity_kg",
        "चोकर आहार की फोटो": "bran_feed_photo",
        "उपलब्ध साइलेज की मात्रा (KG)": "silage_quantity_kg",
        "साइलेज की फोटो": "silage_photo",
        "गोवंश के विचरण के लिए खुले मैदान की स्थिति": "grazing_field_status",
        "उपलब्ध मैदान का क्षेत्रफल ( हे में)": "grazing_field_area_ha",
        "संबंध चारागाह का नाम": "pasture_name",
        "संबंध चारागाह का क्षेत्रफल ( हेक्टर में)": "pasture_area_ha",
        "संबंध चारागाह में चारा फसल बुवाई क्षेत्रफल ( हेक्टर में)": "pasture_crop_area_ha",
        "चरागाह एव फसल की फोटो": "pasture_crop_photo",
        "गोबर निस्तारण की स्थिति": "dung_disposal_status",
        "मौजूद पशुओं के स्वास्थ्य की स्थिति": "animal_health_status",
        "ख़राब स्वाथ्य वाले पशुओं की संख्या": "sick_animal_count",
        "बीमार पशु का ईयर टैग स्कैन करें": "sick_tag_scan",
        "ख़राब स्वाथ्य वाले पशुओं के ईयर टैग": "sick_animal_tags",
        "उपलब्ध दवाओं का चयन करें ": "available_medicines",
        "अस्वस्थ जानवरों की फोटो": "sick_animals_photo",
        "मौजूद पशुओं के टीकाकरण की स्थिति": "vaccination_status",
        "टीकाकरण वाले पशुओं की संख्या": "vaccinated_animals",
        "टीकों का चयन करें ": "vaccine_types",
        "आखरी टीकाकरण का दिनांक": "last_vaccine_date",
        "आखरी कीट नियंत्रण छिड़काव का दिनांक": "last_pest_spray_date",
        "किस माह तक फण्ड रिक्वेस्ट की गई": "fund_requested_till",
        "निरीक्षण आख्या पोर्टल पर अपलोड की गई या नहीं": "report_uploaded",
        "पिछले माह मृत गोवंश की संख्या": "prev_month_dead_count",
        "पिछले माह मृत गोवंश के उपलब्ध पोस्टमार्टम की संख्या": "prev_month_postmortem_count",
        "मृत पशुओं के शव के निस्तारण की स्थिति": "dead_disposal_status_1",
        "मृत पशुओं के शव के निस्तारण की स्थिति ": "dead_disposal_status_2",
        "गौशाला का सुरक्षा प्रबंधन": "security_management",
        "कुल केयर टेकर की संख्या": "total_caretakers",
        "रात्रि में केयर टेकर की संख्या": "night_caretakers",
        "कुल CCTV की संख्या": "cctv_count",
        "CCTV की रिकॉर्डिंग (दिवस)": "cctv_days",
        "सभी केयर टेकर की फोटो": "caretakers_photo",
        "किस माह तक केयर टेकर को तनख्वाह दी जा चुकी है": "salary_paid_till",
        "गोशाला पर मौजूद रजिस्टर": "register_main",
        "अन्य रजिस्टर का नाम एव विवरण दे": "register_other",
        "सहभागिता के अंतर्गत संरक्षित गोवंश की संख्या": "participation_cattle_count",
        "सहभागिता के अंतर्गत लाभान्वित परिवारों की संख्या": "participation_family_count",
        "किस माह तक सहभागिता की राशि का भुगतान हो चुका है": "participation_paid_till",
        "पोषण मिशन के अंतर्गत संरक्षित गोवंश की संख्या": "nutrition_cattle_count",
        "पोषण मिशन के अंतर्गत लाभान्वित परिवारों की संख्या": "nutrition_family_count",
        "किस माह तक पोषण माह की राशि का भुगतान हो चुका है": "nutrition_paid_till",
        "अन्य रिमार्क": "remarks",
        "UID टैग": "uid_tag",
        "विकास खण्ड": "participant_block_name",
        "राजस्व गांव का नाम": "participant_village_name",
        "गोशाला का नाम": "participant_shelter_name",
        "शाहभागी का नाम": "participant_name",
        "शाहभागी का मोबाइल नंबर": "participant_mobile",
        "शाहभागी का आधार नंबर": "participant_aadhar",
        "शाहभागी का पता": "participant_address",
        "ईयर टैग स्कैन करें": "participant_ear_tag_scan",
        "शाहभागिता टैग UID": "participant_tag_uid",
        "Date": "date",
        "Time": "time",
        "GPS Location inspection ": "gps_location_inspection",
    }
    
    # -------------------------------
    # Hardcoded KPI groups (as provided)
    # -------------------------------
    KPI_GROUPS = {
        "inspection_basic": [
            "created_at", "goshala_type", "available_cattle", "remarks",
            "date", "time", "gps_location_inspection", "total_eartagged_cattle"
        ],
        "inspection_officer": [
            "inspector_type", "inspector_designation", "officer_name", "officer_mobile",
            "inspection_type", "shelter_category", "block_name_static",
            "shelter_name_static", "village_name_static"
        ],
        "static_data": [
            "shelter_capacity_static", "protected_cattle_static", "ear_tag_count_static",
            "castration_count_static", "dead_animals_count_static", "artificial_insemination_count_static",
            "handover_cattle_static", "beneficiary_count_static", "gps_location_static"
        ],
        "inspection_shed": [
            "shed_count", "fan_count", "roofed_shed_count", "shed_spray_status", "ventilation_status",
            "cleanliness_arrangement", "shed_photo", "total_shed_area_sqft", "max_capacity",
            "shed_adequate_animals_1", "shed_adequate_animals_2", "additional_shed_status",
            "additional_shed_current_status"
        ],
        "inspection_water": [
            "drinking_water", "water_storage_capacity_litre", "water_source_photo"
        ],
        "inspection_fodder": [
            "fodder_godown_count", "temp_shed_count", "fodder_quantity_quintal",
            "fodder_days_available", "fodder_photo", "bran_feed_quantity_kg",
            "bran_feed_photo", "silage_quantity_kg", "silage_photo"
        ],
        "inspection_pasture": [
            "grazing_field_status", "grazing_field_area_ha", "pasture_name",
            "pasture_area_ha", "pasture_crop_area_ha", "pasture_crop_photo"
        ],
        "inspection_health": [
            "dung_disposal_status", "animal_health_status", "sick_animal_count",
            "sick_tag_scan", "sick_animal_tags", "available_medicines",
            "sick_animals_photo"
        ],
        "inspection_vaccination": [
            "vaccination_status", "vaccinated_animals", "vaccine_types",
            "last_vaccine_date", "last_pest_spray_date"
        ],
        "inspection_admin": [
            "fund_requested_till", "report_uploaded", "register_main", "register_other"
        ],
        "inspection_dead_animals": [
            "prev_month_dead_count", "prev_month_postmortem_count",
            "dead_disposal_status_1"
        ],
        "inspection_security": [
            "security_management", "total_caretakers", "night_caretakers", "cctv_count",
            "cctv_days", "caretakers_photo", "salary_paid_till"
        ],
        "inspection_sahbhagita": [
            "participation_cattle_count", "participation_family_count", "participation_paid_till"
        ],
        "inspection_poshan_mission": [
            "nutrition_cattle_count", "nutrition_family_count", "nutrition_paid_till"
        ],
        "inspection_sahbhagita_details": [
            "uid_tag", "participant_block_name", "participant_village_name", "participant_shelter_name",
            "participant_name", "participant_mobile", "participant_aadhar", "participant_address"
        ],
        "sahbhagita_inspection_details": [
            "participant_ear_tag_scan", "participant_tag_uid", "participant2_block_name",
            "participant2_village_name", "participant2_shelter_name", "participant2_name",
            "participant2_mobile", "participant2_aadhar", "participant2_address"
        ],
    }
    
    # -------------------------------
    # Utility functions
    # -------------------------------
    @st.cache_data
    def load_csv_from_gsheet(csv_url: str) -> pd.DataFrame:
        try:
            return pd.read_csv(csv_url)
        except Exception as e:
            st.error(f"Failed to load Google Sheet CSV: {e}")
            return pd.DataFrame()
    
    @st.cache_data
    def load_static_local(path: str) -> pd.DataFrame:
        try:
            return pd.read_excel(path)
        except Exception:
            return pd.DataFrame()
    
    def safe_rename(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
        present_map = {k: v for k, v in mapping.items() if k in df.columns}
        return df.rename(columns=present_map)
    
    def ensure_date_col(df: pd.DataFrame):
        # prefer existing renamed 'date', else try Created At / created_at
        if "date" in df.columns:
            try:
                df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
                return df
            except Exception:
                pass
        for c in ["Created At", "created_at", "CreatedAt", "Created"]:
            if c in df.columns:
                try:
                    df["date"] = pd.to_datetime(df[c], errors="coerce").dt.date
                    return df
                except Exception:
                    pass
        # fallback: try to parse created_at column if available
        if "created_at" in df.columns:
            try:
                df["date"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date
                return df
            except Exception:
                pass
        df["date"] = pd.NaT
        return df
    
    def prefix_cols_lower(df: pd.DataFrame, cols):
        for c in cols:
            if c in df.columns:
                df[c] = df[c].astype(str).str.strip()
    
    # Performance category helper
    def perf_category(value, higher_is_better=True):
        # value expected between 0-100 (percentage) or normalized KPI
        try:
            v = float(value)
        except:
            return "unknown"
        if higher_is_better:
            if v >= 80:
                return "good"
            elif v >= 50:
                return "moderate"
            else:
                return "poor"
        else:
            # for KPIs where lower is better (e.g., dead animals)
            if v <= 20:
                return "good"
            elif v <= 50:
                return "moderate"
            else:
                return "poor"
    
    # PDF helpers
    def fig_to_png_bytes(fig):
        """Try to export a plotly figure to PNG bytes. Requires kaleido."""
        try:
            img_bytes = fig.to_image(format="png", scale=2)
            return img_bytes
        except Exception as e:
            # fallback: empty bytes
            return None
    
    def add_image_to_pdf(pdf: FPDF, img_bytes, w=180):
        if not img_bytes:
            return
        tmp_b = BytesIO(img_bytes)
        pdf.image(tmp_b, x=None, y=None, w=w)
    
    def df_to_csv_bytes(df):
        return df.to_csv(index=False).encode("utf-8")
    
    # -------------------------------
    # Load data
    # -------------------------------
    with st.spinner("Loading inspection data..."):
        df_inspect = load_csv_from_gsheet(GSHEET_CSV_URL)
    
    # ---------------------------------------
    # 🐄 LOAD & RENAME STATIC DATA
    # ---------------------------------------
    static_df = load_static_local(LOCAL_STATIC_PATH)
    
    if not static_df.empty:
        # --- Normalize column headers ---
        static_df.columns = static_df.columns.str.strip()
    
        # --- Rename Hindi → English (based on your actual file structure) ---
        STATIC_COL_RENAME = {
            "विकास खंड या नगर निकाय": "block_ulb_base",
            "गांव / गोवंश आश्रय स्थल का प्रकार": "shelter_category_base",
            "गांव / गोवंश आश्रय स्थल का नाम": "shelter_name_base",
            "गोवंश संरक्षित की क्षमता": "shelter_capacity_base",
            "संरक्षित गोंवंश": "protected_cattle_base",
            "ईअर टेगिंग की संख्या": "ear_tag_count_base",
            "बधियाकरण" : "count_castaration_base",
            "मृत पशुओं की संख्या" : "count_dead_animal_base",
            "कृत्रिम गर्भाधान": "count_artificial_insemination_base",
            "सुपर्दगी गोवंश" : "count_sahbhagita_animals_base",
            "लाभार्थियों की संख्या" : "count_sahbhagita_beneficiary_base",
            "GPS Location": "gps_location_base",
        }
    
        # --- Apply renaming safely ---
        present_static_map = {k: v for k, v in STATIC_COL_RENAME.items() if k in static_df.columns}
        static_df.rename(columns=present_static_map, inplace=True)
    
        # --- Clean and standardize ---
        for col in ["block_name_static", "shelter_name_static", "shelter_category"]:
            if col in static_df.columns:
                static_df[col] = (
                    static_df[col]
                    .astype(str)
                    .str.strip()
                    .str.lower()
                    .replace("nan", None)
                )
    
        # --- Display preview ---
        st.success("✅ Static data loaded and renamed successfully!")
        st.dataframe(static_df.head(10))
    else:
        st.warning("⚠️ No local static file found or it’s empty.")
    
    # -------------------------------
    # Data prep
    # -------------------------------
    if df_inspect.empty:
        st.warning("Inspection data not loaded. Check Google Sheet ID or network.")
    else:
        # rename inspection columns
        df_inspect = safe_rename(df_inspect, COL_RENAME)
        df_inspect = ensure_date_col(df_inspect)
    
        # clean string columns
        prefix_cols_lower(df_inspect, ["block_name_static", "shelter_name_static", "shelter_category", "officer_name"])
    
        # drop duplicate columns if any
        df_inspect = df_inspect.loc[:, ~df_inspect.columns.duplicated()]
    
        # numeric conversions for typical KPIs if present
        for c in ["available_cattle", "protected_cattle_static", "ear_tag_count_static",
                  "sick_animal_count", "dead_animals_count_static", "total_eartagged_cattle"]:
            if c in df_inspect.columns:
                df_inspect[c] = pd.to_numeric(df_inspect[c], errors="coerce")
    
    # static data rename & cleanup if present
    if not static_df.empty:
        static_df = safe_rename(static_df, COL_RENAME)
        prefix_cols_lower(static_df, ["block_name_static", "shelter_name_static", "shelter_category"])
        static_df = static_df.loc[:, ~static_df.columns.duplicated()]
    
    # -------------------------------
    # Global filter options (available to all tabs)
    # -------------------------------
    blocks = []
    if "block_name_static" in df_inspect.columns:
        blocks = sorted(df_inspect["block_name_static"].dropna().unique().tolist())
    elif not static_df.empty and "block_name_static" in static_df.columns:
        blocks = sorted(static_df["block_name_static"].dropna().unique().tolist())
    
    shelter_types = []
    if "shelter_category" in df_inspect.columns:
        shelter_types = sorted(df_inspect["shelter_category"].dropna().unique().tolist())
    elif not static_df.empty and "shelter_category" in static_df.columns:
        shelter_types = sorted(static_df["shelter_category"].dropna().unique().tolist())
    
    officers = []
    if "officer_name" in df_inspect.columns:
        officers = sorted(df_inspect["officer_name"].dropna().unique().tolist())
    
    # -------------------------------
    # TOP-FILTERS (placed inline above tabs)
    # -------------------------------
    st.title("🐄 Goshala Inspection Dashboard — Government of Uttar Pradesh")
    st.markdown("### Filters (apply to all tabs)")
    
    # Date range global - use df_inspect date column if available
    if "date" in df_inspect.columns:
        min_date = pd.to_datetime(df_inspect["date"], errors="coerce").min()
        max_date = pd.to_datetime(df_inspect["date"], errors="coerce").max()
    else:
        min_date = date.today()
        max_date = date.today()
    
    col_a, col_b, col_c, col_d = st.columns([2,2,2,2])
    start_date = col_a.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date, key="global_start")
    end_date = col_b.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date, key="global_end")
    selected_block = col_c.selectbox("Block / Jurisdiction", ["All"] + blocks, key="global_block")
    selected_type = col_d.selectbox("Shelter Type", ["All"] + shelter_types, key="global_type")
    
    # officer filter (small)
    col_e, col_f = st.columns([2,2])
    selected_officer = col_e.selectbox("Officer", ["All"] + officers, key="global_officer")
    refresh_btn = col_f.button("Refresh Data")
    
    if refresh_btn:
        st.experimental_rerun()
    
    # Apply global date + block + type + officer filters to create df_base used across tabs
    if not df_inspect.empty:
        df_base = df_inspect.copy()
        # apply date filter
        if start_date:
            df_base = df_base[pd.to_datetime(df_base["date"], errors="coerce") >= pd.to_datetime(start_date)]
        if end_date:
            df_base = df_base[pd.to_datetime(df_base["date"], errors="coerce") <= pd.to_datetime(end_date)]
        # block filter
        if selected_block != "All" and "block_name_static" in df_base.columns:
            df_base = df_base[df_base["block_name_static"] == selected_block]
        # shelter type
        if selected_type != "All" and "shelter_category" in df_base.columns:
            df_base = df_base[df_base["shelter_category"] == selected_type]
        # officer
        if selected_officer != "All" and "officer_name" in df_base.columns:
            df_base = df_base[df_base["officer_name"] == selected_officer]
    else:
        df_base = pd.DataFrame()
    
    # helper: which columns to present often
    def cols_for_table():
        cols = ["date", "block_name_static", "shelter_name_static", "shelter_category", "officer_name"]
        extra = [c for group in KPI_GROUPS.values() for c in group if c in df_base.columns]
        cols.extend(extra)
        # ensure unique and existing
        cols = [c for c in dict.fromkeys(cols) if c in df_base.columns]
        return cols
    
    # -------------------------------
    # Tabs
    # -------------------------------
    tabs = st.tabs(["Overview", "Jurisdiction", "Officer", "KPI Groups", "Map", "Leaderboards"])
    
    # -------------------------------
    # TAB 1: Overview
    # -------------------------------
    with tabs[0]:
        st.header("📅 Overview — Last Inspections")
    
        df_range = df_base.copy()
        if df_range.empty:
            st.info("No inspection rows in selected filters/date range.")
        else:
            # --- Ensure static and inspection datasets are harmonized ---
            # --- Robust static vs inspected coverage calculation (replace existing block) ---
            # ===================================================
            # 🧭 OVERVIEW — Static vs Inspection Coverage (Fixed)
            # ===================================================
    
            import re
            from difflib import get_close_matches
    
            st.subheader("📊 Inspection Coverage Summary")
    
            # --- Helper: normalize shelter names ---
            def normalize_name(x):
                if pd.isna(x):
                    return None
                s = str(x).strip().lower()
                s = re.sub(r"[^\w\s]", " ", s)
                s = re.sub(r"\s+", " ", s).strip()
                return s if s else None
    
            # --- Detect available columns ---
            inspect_col = None
            for c in ["shelter_name_static", "shelter_name", "village_name_static"]:
                if c in df_range.columns:
                    inspect_col = c
                    break
    
            static_col = None
            for c in [
                "shelter_name_base",
                "गोशाला का नाम",
                "गांव / गोवंश आश्रय स्थल का नाम",
            ]:
                if c in static_df.columns:
                    static_col = c
                    break
    
            # --- Normalize names ---
            if static_col and not static_df.empty:
                static_df["_norm_shelter"] = static_df[static_col].map(normalize_name)
                static_unique = static_df["_norm_shelter"].dropna().unique().tolist()
            else:
                static_unique = []
    
            if inspect_col and not df_range.empty:
                df_range["_norm_shelter"] = df_range[inspect_col].map(normalize_name)
                inspected_unique = df_range["_norm_shelter"].dropna().unique().tolist()
            else:
                inspected_unique = []
    
            # --- Coverage computation ---
            if static_unique:
                total_shelters = len(static_unique)
                # Direct matches
                matched = [s for s in inspected_unique if s in static_unique]
                direct_count = len(matched)
    
                # Fuzzy match fallback for slightly different names
                unmatched = [s for s in inspected_unique if s not in static_unique]
                fuzzy_matched = []
                for s in unmatched:
                    close = get_close_matches(s, static_unique, n=1, cutoff=0.75)
                    if close:
                        fuzzy_matched.append((s, close[0]))
    
                fuzzy_count = len(set([x[1] for x in fuzzy_matched]))
                inspected_total = direct_count + fuzzy_count
                coverage = round((inspected_total / total_shelters) * 100, 2)
            else:
                total_shelters = len(inspected_unique)
                inspected_total = total_shelters
                coverage = 100.0
    
            # --- Display key metrics ---
            c1, c2, c3 = st.columns(3)
            c1.metric("🏠 Total Shelters (Static)", total_shelters)
            c2.metric("🔍 Inspected (Selected Range)", inspected_total)
            c3.metric("📈 Coverage (%)", f"{coverage}%")
    
            # --- Optional: show missing / matched shelters ---
            with st.expander("🔎 View Matching Debug Info"):
                st.write(f"Static shelter column used: `{static_col}`")
                st.write(f"Inspection shelter column used: `{inspect_col}`")
                st.write(f"Direct matches: {direct_count}, Fuzzy matches: {fuzzy_count}")
                st.write(f"Total inspected (effective): {inspected_total}")
                if fuzzy_matched:
                    st.dataframe(pd.DataFrame(fuzzy_matched, columns=["inspected_norm", "static_norm_match"]).head(10))
    
            
    
            # ===== Replacement: Interactive pie chart (robust column detection) =====
            import altair as alt
            import re
            from typing import Optional
    
            st.subheader("🥧 Inspection Coverage by Type / Jurisdiction / Officer (robust)")
    
            # --- helper to detect a column from candidates ---
            def detect_col(df: pd.DataFrame, candidates):
                for c in candidates:
                    if c in df.columns:
                        return c
                return None
    
            # --- candidates (inspection / base / static variations) ---
            type_candidates_inspect = ["shelter_category_base", "shelter_category", "shelter_category_static"]
            block_candidates_inspect = ["block_ulb_base", "block_name_static", "block_name", "block_ulb"]
            officer_candidates_inspect = ["officer_name", "inspector_name", "officer"]
            shelter_candidates_inspect = ["shelter_name_static", "shelter_name", "village_name_static", "village_name"]
    
            type_col = detect_col(df_range, type_candidates_inspect) or None
            block_col = detect_col(df_range, block_candidates_inspect) or None
            officer_col = detect_col(df_range, officer_candidates_inspect) or None
            inspect_shelter_col = detect_col(df_range, shelter_candidates_inspect) or None
    
            # static candidates (for total shelters)
            shelter_candidates_static = ["shelter_name_base", "shelter_name_static", "shelter_name", "गोशाला का नाम"]
            static_shelter_col = detect_col(static_df, shelter_candidates_static) if static_df is not None and not static_df.empty else None
    
            # --- build dropdown options safely ---
            def safe_options(df: pd.DataFrame, col: Optional[str]):
                if col and col in df.columns:
                    vals = sorted(pd.Series(df[col].dropna().astype(str)).unique().tolist())
                    return ["All"] + vals if vals else ["All"]
                return ["All"]
    
            type_options = safe_options(df_range, type_col)
            block_options = safe_options(df_range, block_col)
            officer_options = safe_options(df_range, officer_col)
    
            c1, c2, c3 = st.columns(3)
            selected_type = c1.selectbox("Shelter Type", options=type_options, index=0, key="ov_type_select")
            selected_block = c2.selectbox("Jurisdiction (Block / ULB)", options=block_options, index=0, key="ov_block_select")
            selected_officer = c3.selectbox("Inspection Officer", options=officer_options, index=0, key="ov_officer_select")
    
            # --- apply filters to df_range copy ---
            df_filtered = df_range.copy()
            if selected_type != "All" and type_col:
                df_filtered = df_filtered[df_filtered[type_col].astype(str) == selected_type]
            if selected_block != "All" and block_col:
                df_filtered = df_filtered[df_filtered[block_col].astype(str) == selected_block]
            if selected_officer != "All" and officer_col:
                df_filtered = df_filtered[df_filtered[officer_col].astype(str) == selected_officer]
    
            # --- normalize names helper ---
            def normalize_name(x):
                if pd.isna(x):
                    return None
                s = str(x).strip().lower()
                s = re.sub(r"[^\w\s]", " ", s)
                s = re.sub(r"\s+", " ", s).strip()
                return s if s else None
    
            # --- lists for matching ---
            if static_shelter_col and static_df is not None and not static_df.empty:
                static_df["_norm_shelter"] = static_df[static_shelter_col].map(normalize_name)
                static_unique = [s for s in static_df["_norm_shelter"].dropna().unique()]
            else:
                static_unique = []
    
            if inspect_shelter_col and not df_filtered.empty:
                df_filtered["_norm_shelter"] = df_filtered[inspect_shelter_col].map(normalize_name)
                inspected_unique = [s for s in df_filtered["_norm_shelter"].dropna().unique()]
            else:
                inspected_unique = []
    
            # --- compute counts ---
            if static_unique:
                total_shelters = len(static_unique)
                inspected_count = len([s for s in inspected_unique if s in static_unique])
                not_inspected = max(total_shelters - inspected_count, 0)
            else:
                # fallback: use unique inspected as total (no static available)
                total_shelters = len(inspected_unique)
                inspected_count = total_shelters
                not_inspected = 0
    
            coverage_pct = (inspected_count / total_shelters * 100) if total_shelters else 0.0
    
            # --- pie chart data ---
            pie_df = pd.DataFrame({
                "Status": ["Inspected", "Not Inspected"],
                "Count": [inspected_count, not_inspected]
            })
    
            st.markdown(f"### 📊 Coverage: {coverage_pct:.1f}% ({inspected_count} / {total_shelters})")
    
            # ensure valid pie (avoid negative or all-zero)
            if pie_df["Count"].sum() == 0:
                st.info("No shelters available for selected filters to display coverage.")
            else:
                pie_chart = (
                    alt.Chart(pie_df)
                    .mark_arc(innerRadius=60)
                    .encode(
                        theta=alt.Theta(field="Count", type="quantitative"),
                        color=alt.Color(field="Status", type="nominal", scale=alt.Scale(scheme="category10")),
                        tooltip=["Status", "Count"]
                    )
                    .properties(height=320)
                )
                st.altair_chart(pie_chart, use_container_width=True)
    
            # --- details in expander ---
            with st.expander("📋 Coverage details"):
                st.write(f"Total shelters (static): {total_shelters}")
                st.write(f"Inspected (effective): {inspected_count}")
                st.write(f"Not inspected: {not_inspected}")
                st.write("Inspection rows (sample):")
                st.dataframe(df_filtered[[inspect_shelter_col, type_col, block_col, officer_col]].head(50) if inspect_shelter_col else df_filtered.head(50))
    
            # KPI group quick summary (small table + selectable KPI)
            st.subheader("KPI Group Quick Summary")
            group_choice = st.selectbox("Choose KPI Group", list(KPI_GROUPS.keys()), key="overview_group_choice")
            kpi_cols = [c for c in KPI_GROUPS[group_choice] if c in df_range.columns]
            if kpi_cols:
                # convert numeric ones
                numeric = []
                for c in kpi_cols:
                    is_num = pd.api.types.is_numeric_dtype(df_range[c])
                    if not is_num and df_range[c].dtype == "object":
                        try:
                            is_num = df_range[c].dropna().astype(str).str.replace(".", "", regex=False).str.isnumeric().any()
                        except Exception:
                            is_num = False
                    if is_num:
                        try:
                            df_range[c] = pd.to_numeric(df_range[c], errors="coerce")
                        except Exception:
                            pass
    
                    
                    
                        try:
                            df_range[c] = pd.to_numeric(df_range[c], errors="coerce")
                        except:
                            pass
                    if pd.api.types.is_numeric_dtype(df_range[c]):
                        numeric.append(c)
                if numeric:
                    kpi_summary = df_range[numeric].agg(["count", "mean", "sum"]).T.reset_index().rename(columns={"index": "kpi"})
                    st.dataframe(kpi_summary)
                    sel_kpi = st.selectbox("Select KPI to plot (Overview)", numeric, key="overview_kpi_plot")
                    # trend over time - mean per date
                    trend = df_range.copy()
                    trend["date"] = pd.to_datetime(trend["date"])
                    trend_k = trend.groupby("date")[sel_kpi].mean().reset_index()
                    fig = px.line(trend_k, x="date", y=sel_kpi, title=f"Trend: {sel_kpi}", markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric KPIs in selected group for current filters.")
            else:
                st.info("No columns found for this KPI group in filtered data.")
    
            # show sample rows and allow CSV export
            st.subheader("Filtered inspection rows (sample)")
            showc = cols_for_table()
            st.dataframe(df_range[showc].sort_values(by="date", ascending=False).reset_index(drop=True).head(200))
            csv = df_range.to_csv(index=False).encode("utf-8")
            st.download_button("Download filtered CSV", data=csv, file_name="goshala_inspections_filtered.csv", mime="text/csv")
    
            # PDF generation (Overview includes link to generate full PDF across all tabs)
            st.markdown("### Reports")
            if st.button("Generate PDF Report (all tabs)"):
                with st.spinner("Generating PDF. This may take a few seconds..."):
                    # Build PDF (fpdf)
                    pdf = FPDF(orientation="P", unit="mm", format="A4")
                    pdf.set_auto_page_break(auto=True, margin=10)
                    # Title page
                    pdf.add_page()
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 8, "🐄 Goshala Inspection Dashboard — Government of Uttar Pradesh", ln=True)
                    pdf.ln(4)
                    pdf.set_font("Arial", size=10)
                    pdf.cell(0, 6, f"Date range: {start_date} to {end_date}", ln=True)
                    pdf.cell(0, 6, f"Filters: Block={selected_block} | Type={selected_type} | Officer={selected_officer}", ln=True)
                    pdf.ln(6)
    
                    # Overview metrics
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 6, "Overview Summary", ln=True)
                    pdf.set_font("Arial", size=10)
                    pdf.cell(0, 6, f"Total shelters: {total_shelters or 'N/A'}", ln=True)
                    pdf.cell(0, 6, f"Inspected (filters): {inspected}", ln=True)
                    pdf.cell(0, 6, f"Coverage (%): {coverage if coverage is not None else 'N/A'}", ln=True)
                    pdf.ln(6)
    
                    # Add timeline chart as image
                    try:
                        img_bytes = None
                        if 'fig' in locals():
                            img_bytes = fig.to_image(format="png", scale=2)
                        if img_bytes:
                            tmp = BytesIO(img_bytes)
                            pdf.image(tmp, w=180)
                    except Exception:
                        pass
    
                    # Add small table as CSV snippet
                    try:
                        sample_csv = df_range.head(10).to_csv(index=False)
                        pdf.set_font("Arial", size=9)
                        pdf.ln(6)
                        pdf.multi_cell(0, 5, sample_csv)
                    except Exception:
                        pass
    
                    # Watermark / footer
                    pdf.set_y(-20)
                    pdf.set_font("Arial", size=8)
                    pdf.cell(0, 5, "Auto-generated via Goshala Analytics, © 2025 Government of Uttar Pradesh", ln=True, align="C")
    
                    # deliver PDF
                    pdf_bytes = pdf.output(dest="S").encode("latin-1")
                    st.download_button("Download PDF report", data=pdf_bytes, file_name=pdf_filename(), mime="application/pdf")
    
    # -------------------------------
    # TAB 2: Jurisdiction Performance
    # -------------------------------
    with tabs[1]:
        st.header("🏢 Jurisdiction Performance")
        df_f = df_base.copy()
        if df_f.empty:
            st.info("No data for selected filters.")
        else:
            sub = st.radio("View:", ["By KPI Group", "By Specific KPI", "By Officer"], horizontal=True, key="juris_view_mode")
    
            if sub == "By KPI Group":
                group = st.selectbox("Select KPI Group", list(KPI_GROUPS.keys()), key="juris_group")
                kcols = [c for c in KPI_GROUPS[group] if c in df_f.columns]
                if not kcols:
                    st.info("No KPI columns from this group found in filtered data.")
                else:
                    # numeric KPI columns
                    numeric_k = []
                    for c in kcols:
                        df_f[c] = pd.to_numeric(df_f[c], errors="coerce")
                        if pd.api.types.is_numeric_dtype(df_f[c]):
                            numeric_k.append(c)
                    if not numeric_k:
                        st.info("No numeric KPIs in this group.")
                    else:
                        # compute means by block
                        if "block_name_static" in df_f.columns:
                            agg = df_f.groupby("block_name_static")[numeric_k].mean().reset_index()
                            st.dataframe(agg)
                            sel_kpi = st.selectbox("Select KPI to visualize", numeric_k, key="juris_group_kpi_select")
                            # heatmap using plotly
                            heat = agg.copy()
                            heat["rank"] = heat[sel_kpi].rank(method="dense", ascending=False)
                            fig = px.bar(heat.sort_values(sel_kpi, ascending=False), x="block_name_static", y=sel_kpi,
                                         color=sel_kpi, color_continuous_scale="Viridis")
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("No block column available for grouping.")
    
            elif sub == "By Specific KPI":
                # choose KPI from all KPI groups
                all_kpis = sorted(list({c for group in KPI_GROUPS.values() for c in group if c in df_f.columns}))
                if not all_kpis:
                    st.info("No KPI columns available in filtered data.")
                else:
                    sel_kpi = st.selectbox("Select KPI", all_kpis, key="juris_specific_kpi")
                    # ensure numeric
                    df_f[sel_kpi] = pd.to_numeric(df_f[sel_kpi], errors="coerce")
                    # group by block
                    if "block_name_static" in df_f.columns:
                        agg = df_f.groupby("block_name_static")[[sel_kpi]].mean().reset_index().sort_values(by=sel_kpi, ascending=False)
                        # interactive bar with altair
                        sel = alt.selection_single(on="click", fields=["block_name_static"], empty="all")
                        chart = alt.Chart(agg).mark_bar().encode(
                            x=alt.X("block_name_static:N", sort="-y", title="Block"),
                            y=alt.Y(f"{sel_kpi}:Q", title=f"Average {sel_kpi}"),
                            color=alt.condition(sel, alt.value("#1f77b4"), alt.value("#d3d3d3")),
                            tooltip=[alt.Tooltip("block_name_static"), alt.Tooltip(sel_kpi, format=".2f")]
                        ).add_params(sel).properties(height=420)
                        st.altair_chart(chart, use_container_width=True)
                        st.dataframe(agg)
                    else:
                        st.info("No block column for grouping.")
            else:
                # By officer: compute KPI group means per officer
                if "officer_name" not in df_f.columns:
                    st.info("No officer data available.")
                else:
                    group = st.selectbox("Select KPI Group", list(KPI_GROUPS.keys()), key="juris_by_officer_group")
                    kcols = [c for c in KPI_GROUPS[group] if c in df_f.columns]
                    numeric_k = []
                    for c in kcols:
                        df_f[c] = pd.to_numeric(df_f[c], errors="coerce")
                        if pd.api.types.is_numeric_dtype(df_f[c]):
                            numeric_k.append(c)
                    if not numeric_k:
                        st.info("No numeric KPIs in this group.")
                    else:
                        agg = df_f.groupby("officer_name")[numeric_k].mean().reset_index()
                        st.dataframe(agg)
                        sel_k = st.selectbox("Select KPI to plot", numeric_k, key="juris_officer_kpi")
                        fig = px.bar(agg.sort_values(sel_k, ascending=False), x="officer_name", y=sel_k, color=sel_k, color_continuous_scale="Plasma")
                        st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------
    # TAB 3: Officer Performance
    # -------------------------------
    with tabs[2]:
        st.header("👮 Officer Performance")
        df_o = df_base.copy()
        if df_o.empty:
            st.info("No data for selected filters.")
        else:
            if "officer_name" not in df_o.columns:
                st.info("Officer column missing.")
            else:
                officer_options = ["All"] + sorted(df_o["officer_name"].dropna().unique().tolist())
                chosen_officer = st.selectbox("Select Officer", officer_options, key="officer_tab_select")
                df_o2 = df_o.copy()
                if chosen_officer != "All":
                    df_o2 = df_o2[df_o2["officer_name"] == chosen_officer]
    
                # inspections count per officer
                count_tbl = df_o2.groupby("officer_name").size().reset_index(name="Inspections").sort_values("Inspections", ascending=False)
                if not count_tbl.empty:
                    sel = alt.selection_single(on="click", fields=["officer_name"], empty="all")
                    bar = alt.Chart(count_tbl).mark_bar().encode(
                        x=alt.X("officer_name:N", sort='-y', title="Officer"),
                        y=alt.Y("Inspections:Q", title="Inspections"),
                        color=alt.condition(sel, alt.value("#1f77b4"), alt.value("#d3d3d3")),
                        tooltip=["officer_name", "Inspections"]
                    ).add_params(sel).properties(height=360)
                    text = bar.mark_text(dy=-5, align="center").encode(text=alt.Text("Inspections:Q", format=".0f"))
                    st.altair_chart(bar + text, use_container_width=True)
                    st.dataframe(count_tbl)
                else:
                    st.info("No inspection counts available.")
    
                # KPI group performance by officer
                st.subheader("KPI Group Performance by Officer")
                chosen_group = st.selectbox("Select KPI Group", list(KPI_GROUPS.keys()), key="officer_group_choice")
                kcols = [c for c in KPI_GROUPS[chosen_group] if c in df_o2.columns]
                numeric_k = []
                for c in kcols:
                    df_o2[c] = pd.to_numeric(df_o2[c], errors="coerce")
                    if pd.api.types.is_numeric_dtype(df_o2[c]):
                        numeric_k.append(c)
                if numeric_k:
                    agg = df_o2.groupby("officer_name")[numeric_k].mean().reset_index()
                    st.dataframe(agg)
                    sel_kpi = st.selectbox("Select KPI to visualize", numeric_k, key="officer_kpi_choice")
                    fig = px.bar(agg.sort_values(sel_kpi, ascending=False), x="officer_name", y=sel_kpi, color=sel_kpi, color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No numeric KPIs for this group and filter.")
    
                # trend for selected officer and KPI
                st.subheader("KPI Trend for selected officer")
                if "date" in df_o2.columns:
                    sel_kpi2 = st.selectbox("Select KPI for trend", [c for c in sum(KPI_GROUPS.values(), []) if c in df_o2.columns], key="officer_trend_kpi")
                    if sel_kpi2:
                        df_o2["date"] = pd.to_datetime(df_o2["date"])
                        trend = df_o2.groupby("date")[[sel_kpi2]].mean().reset_index()
                        fig = px.line(trend, x="date", y=sel_kpi2, markers=True, title=f"{sel_kpi2} over time")
                        st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------
    # TAB 4: KPI Groups deep dive
    # -------------------------------
    with tabs[3]:
        st.header("📚 KPI Groups Explorer")
        df_k = df_base.copy()
        if df_k.empty:
            st.info("No data for selected filters.")
        else:
            group = st.selectbox("Choose KPI Group", list(KPI_GROUPS.keys()), key="kpi_group_tab")
            kcols = [c for c in KPI_GROUPS[group] if c in df_k.columns]
            if not kcols:
                st.info("No columns for this group in filtered dataset.")
            else:
                # numeric conversion
                for c in kcols:
                    df_k[c] = pd.to_numeric(df_k[c], errors="coerce")
    
                # correlation heatmap for numeric kpis
                numeric_cols = [c for c in kcols if pd.api.types.is_numeric_dtype(df_k[c])]
                if numeric_cols and len(numeric_cols) > 1:
                    corr = df_k[numeric_cols].corr().round(2)
                    fig = px.imshow(corr, text_auto=True, aspect="auto", title="KPI Correlation Matrix")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Not enough numeric KPI columns for correlation matrix.")
    
                # Radar chart (approx) per block for selected KPIs (uses normalization)
                st.subheader("Compare blocks on selected KPIs")
                sel_kpis = st.multiselect("Select KPIs (2-6)", numeric_cols[:6], default=numeric_cols[:4], key="kpis_radar")
                if sel_kpis and len(sel_kpis) >= 2:
                    if "block_name_static" in df_k.columns:
                        agg = df_k.groupby("block_name_static")[sel_kpis].mean().reset_index()
                        # normalize each column 0-1
                        norm = agg.copy()
                        for c in sel_kpis:
                            mn = norm[c].min()
                            mx = norm[c].max()
                            if mx - mn == 0:
                                norm[c] = 0.5
                            else:
                                norm[c] = (norm[c] - mn) / (mx - mn)
                        # show top 3 blocks by average
                        norm["avg"] = norm[sel_kpis].mean(axis=1)
                        top_blocks = norm.sort_values("avg", ascending=False).head(3)
                        for _, r in top_blocks.iterrows():
                            fig = px.line_polar(r[sel_kpis].values.reshape(1, -1), r=[float(x) for x in r[sel_kpis]], theta=sel_kpis, line_close=True)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No block column for comparison.")
                else:
                    st.info("Select at least 2 KPIs for comparison.")
    
    # -------------------------------
    # TAB 5: Interactive Map (Plotly)
    # -------------------------------
    with tabs[4]:
        st.header("🗺️ Interactive Map")
        df_m = df_base.copy()
        if df_m.empty:
            st.info("No data for selected filters.")
        else:
            gps_col = None
            if "gps_location_inspection" in df_m.columns:
                gps_col = "gps_location_inspection"
            elif "gps_location_static" in df_m.columns:
                gps_col = "gps_location_static"
    
            if gps_col is None:
                st.info("No GPS location column available for mapping.")
            else:
                # parse GPS -> lat, lon
                def parse_gps(val):
                    try:
                        s = str(val)
                        s = s.replace("(", "").replace(")", "")
                        parts = [p.strip() for p in s.split(",") if p.strip() != ""]
                        if len(parts) >= 2:
                            return float(parts[0]), float(parts[1])
                    except:
                        pass
                    return np.nan, np.nan
    
                df_m["lat"], df_m["lon"] = zip(*df_m[gps_col].astype(str).map(parse_gps))
                df_map = df_m.dropna(subset=["lat", "lon"]).copy()
                if df_map.empty:
                    st.info("No valid GPS records found after parsing.")
                else:
                    # Choose map mode
                    map_mode = st.selectbox("Map Mode", ["Inspection coverage", "KPI Group mean", "Specific KPI"], key="map_mode")
                    if map_mode == "Inspection coverage":
                        # marker color = inspected (all rows shown as points) - categorize by recency or presence
                        df_map["last_date"] = pd.to_datetime(df_map["date"])
                        # performance: inspected in selected range -> all are inspected; show recent vs older
                        df_map["days_from_end"] = (pd.to_datetime(end_date) - df_map["last_date"]).dt.days
                        df_map["recency_cat"] = df_map["days_from_end"].apply(lambda x: "recent" if x <= 30 else "older")
                        fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="shelter_name_static", color="recency_cat",
                                                color_discrete_map={"recent":"green","older":"orange"}, zoom=6, height=700)
                        fig.update_layout(mapbox_style="open-street-map")
                        st.plotly_chart(fig, use_container_width=True)
                    elif map_mode == "KPI Group mean":
                        group = st.selectbox("Select KPI Group", list(KPI_GROUPS.keys()), key="map_group")
                        kcols = [c for c in KPI_GROUPS[group] if c in df_map.columns]
                        # compute mean per shelter or per block (we'll do per shelter)
                        if kcols:
                            numeric = []
                            for c in kcols:
                                df_map[c] = pd.to_numeric(df_map[c], errors="coerce")
                                if pd.api.types.is_numeric_dtype(df_map[c]):
                                    numeric.append(c)
                            if numeric:
                                df_map["kpi_mean"] = df_map[numeric].mean(axis=1)
                                # color scale
                                fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="shelter_name_static", color="kpi_mean",
                                                        color_continuous_scale="RdYlGn", zoom=6, height=700)
                                fig.update_layout(mapbox_style="open-street-map")
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("No numeric KPIs in selected group for mapping.")
                        else:
                            st.info("No KPIs for this group present in map data.")
                    else:
                        # specific KPI
                        all_kpis = sorted([c for group in KPI_GROUPS.values() for c in group if c in df_map.columns])
                        sel_kpi = st.selectbox("Select KPI for map", all_kpis, key="map_specific_kpi")
                        df_map[sel_kpi] = pd.to_numeric(df_map[sel_kpi], errors="coerce")
                        if df_map[sel_kpi].dropna().empty:
                            st.info("No numeric values for selected KPI.")
                        else:
                            fig = px.scatter_mapbox(df_map, lat="lat", lon="lon", hover_name="shelter_name_static", color=sel_kpi,
                                                    color_continuous_scale="Viridis", zoom=6, height=700)
                            fig.update_layout(mapbox_style="open-street-map")
                            st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------
    # TAB 6: Leaderboards
    # -------------------------------
    with tabs[5]:
        st.header("🏆 Leaderboards")
        df_l = df_base.copy()
        if df_l.empty:
            st.info("No data for selection.")
        else:
            mode = st.radio("Mode", ["Cumulative", "KPI Group", "Specific KPI"], horizontal=True, key="leader_mode")
            block_col = "block_name_static" if "block_name_static" in df_l.columns else None
    
            if mode == "Cumulative":
                if block_col:
                    lb = df_l.groupby(block_col).size().reset_index(name="Inspections").sort_values("Inspections", ascending=False)
                    st.subheader("Top Performing Jurisdictions (by inspection count)")
                    st.dataframe(lb.head(10))
                else:
                    st.info("No block column available.")
    
            elif mode == "KPI Group":
                group = st.selectbox("Choose KPI Group", list(KPI_GROUPS.keys()), key="leader_group")
                kcols = [c for c in KPI_GROUPS[group] if c in df_l.columns]
                numeric = []
                for c in kcols:
                    df_l[c] = pd.to_numeric(df_l[c], errors="coerce")
                    if pd.api.types.is_numeric_dtype(df_l[c]):
                        numeric.append(c)
                if numeric and block_col:
                    agg = df_l.groupby(block_col)[numeric].mean().reset_index()
                    # create an overall score = mean of normalized KPI columns
                    df_norm = agg.copy()
                    for c in numeric:
                        mn = df_norm[c].min(); mx = df_norm[c].max()
                        if pd.isna(mn) or pd.isna(mx) or mx == mn:
                            df_norm[c] = 0.5
                        else:
                            df_norm[c] = (df_norm[c] - mn) / (mx - mn)
                    df_norm["score"] = df_norm[numeric].mean(axis=1)
                    df_norm = df_norm.sort_values("score", ascending=False)
                    st.subheader("Top jurisdictions (by KPI group composite score)")
                    st.dataframe(df_norm[[block_col, "score"] + numeric].head(10))
                    st.subheader("Bottom jurisdictions")
                    st.dataframe(df_norm[[block_col, "score"] + numeric].tail(10))
                else:
                    st.info("No numeric KPIs or block column available for KPI Group mode.")
    
            else:
                # specific KPI
                all_kpis = sorted([c for group in KPI_GROUPS.values() for c in group if c in df_l.columns])
                if not all_kpis:
                    st.info("No KPIs available for leaderboard.")
                else:
                    sel_kpi = st.selectbox("Select KPI", all_kpis, key="leader_specific_kpi")
                    df_l[sel_kpi] = pd.to_numeric(df_l[sel_kpi], errors="coerce")
                    if block_col:
                        agg = df_l.groupby(block_col)[sel_kpi].mean().reset_index().sort_values(sel_kpi, ascending=False)
                        st.subheader("Top jurisdictions")
                        st.dataframe(agg.head(10))
                        st.subheader("Lowest jurisdictions")
                        st.dataframe(agg.tail(10))
                    else:
                        st.info("No block column for grouping.")
    
    
    
    import io
    import pandas as pd
    import streamlit as st
    from datetime import datetime
    
    # Assuming your dataframe is called df and already loaded from Google Sheet
    
    st.markdown("---")
    st.subheader("📅 Date Range & Data Download")
    
    # --- DATE RANGE SELECTOR ---
    min_date = pd.to_datetime(df_inspect['date']).min() if 'date' in df_inspect.columns else datetime(2024, 1, 1)
    max_date = pd.to_datetime(df_inspect['date']).max() if 'date' in df_inspect.columns else datetime.now()
    
    start_date, end_date = st.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len([start_date, end_date]) == 2:
        filtered_df = df_inspect[
            (pd.to_datetime(df_inspect['date']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(df_inspect['date']) <= pd.to_datetime(end_date))
        ]
    else:
        filtered_df = df_inspect.copy()
    
    st.write(f"Showing records from **{start_date}** to **{end_date}**")
    st.dataframe(filtered_df)
    
    # --- PDF REPORT DOWNLOAD SECTION (existing) ---
    st.markdown("### 📄 Generate PDF Report")
    # (your existing PDF generation and download button code here)
    
    # --- EXCEL DOWNLOAD SECTION ---
    st.markdown("### 💾 Download Full Data (Excel)")
    
    def convert_df_to_excel(df):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Data')
        output.seek(0)
        return output.getvalue()
    
    excel_data = convert_df_to_excel(df_inspect)  # entire dataframe, not filtered
    
    st.download_button(
        label="⬇️ Download Complete Data (Excel)",
        data=excel_data,
        file_name=f"goshala_data_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # -------------------------------
    # End of app
    # -------------------------------
    st.markdown("---")
    st.caption("Dashboard generated by Goshala Inspection Dashboard system. PDF footers include watermark. © 2025 Government of Uttar Pradesh")
    
