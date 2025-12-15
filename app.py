import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ================= CONFIG =================
SHEET_ID = "1BX9h3qVC0NA41bi0oMQK3GsvdOjxOBkThQRJobpmeD0"
SHEET_NAME = "Sheet1"

st.set_page_config(page_title="Dashboard IoT Kapal", layout="wide")
st.title("🚢 Dashboard IoT Kapal")
st.caption("Auto refresh tiap 1 menit")

st_autorefresh(interval=60_000, key="refresh")

# ================= GOOGLE SHEET =================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["google_service_account"],
    scope
)

client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ================= LOAD DATA =================
data = sheet.get_all_records()
df = pd.DataFrame(data)

df["waktu"] = pd.to_datetime(df["waktu"])

# pastikan kolom numerik
df["suhu"] = pd.to_numeric(df["suhu"], errors="coerce")
df["getaran"] = pd.to_numeric(df["getaran"], errors="coerce")
df["oli"] = pd.to_numeric(df["oli"], errors="coerce")

# ================= RESAMPLE 5 MENIT =================
df_5m = (
    df.set_index("waktu")[["suhu", "getaran"]]
    .resample("5T")
    .mean()
    .reset_index()
)

# ================= DASHBOARD =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡 Suhu Mesin (°C)")
    st.line_chart(df_5m.set_index("waktu")["suhu"])

with col2:
    st.subheader("📈 Getaran Mesin")
    st.line_chart(df_5m.set_index("waktu")["getaran"])

# ================= STATUS TEKANAN OLI =================
st.subheader("🛢 Status Tekanan Oli")

df["oil_status"] = df["oli"].apply(lambda x: 1 if x == 1 else 0)

st.scatter_chart(
    df.set_index("waktu")["oil_status"]
)
