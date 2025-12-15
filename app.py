import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ================= CONFIG =================
SHEET_ID = "1BX9h3qVC0NA41bi0oMQK3GsvdOjxOBkThQRJobpmeD0"
SHEET_NAME = "Sheet1"

st.set_page_config(
    page_title="Dashboard IoT Kapal",
    layout="wide"
)

st.title("🚢 Dashboard IoT Kapal")
st.caption("Auto refresh tiap 1 menit")

# auto refresh 1 menit
st_autorefresh(interval=60_000, key="refresh")

# ================= GOOGLE SHEET =================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

data = sheet.get_all_records()
df = pd.DataFrame(data)

# ================= PREPROCESS =================
df["waktu"] = pd.to_datetime(df["waktu"])
df = df.sort_values("waktu")

# resample 5 menit
df_5m = (
    df.set_index("waktu")
      .resample("5T")
      .mean(numeric_only=True)
      .reset_index()
)

# ================= GRAFIK =================
col1, col2 = st.columns(2)

with col1:
    st.subheader("🌡 Suhu Mesin (°C)")
    st.line_chart(
        df_5m.set_index("waktu")[["suhu"]],
        use_container_width=True
    )

with col2:
    st.subheader("📈 Getaran Mesin")
    st.line_chart(
        df_5m.set_index("waktu")[["getaran"]],
        use_container_width=True
    )

# ================= STATUS OLI =================
st.subheader("🛢 Status Tekanan Oli")

# 1 = normal, 0 = drop
df_oil = df[["waktu", "oli"]].copy()
df_oil["status_oli"] = df_oil["oli"].apply(lambda x: 1 if x == 1 else 0)

st.line_chart(
    df_oil.set_index("waktu")[["status_oli"]],
    use_container_width=True
)

st.caption("0 = DROP (merah), 1 = NORMAL (hijau)")
