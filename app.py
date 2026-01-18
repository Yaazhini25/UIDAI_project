import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="AQIS",
    layout="wide"
)

# --------------------------------------------------
# LOAD CUSTOM CSS
# --------------------------------------------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# TITLE
# --------------------------------------------------
st.title("Aadhaar Quality Intelligence System (AQIS)")
st.caption("National Real-time Monitoring of Aadhaar Enrollment Center Quality")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_data():
    return pd.read_csv("data/center_quality_intelligence.csv")

df = load_data()

# --------------------------------------------------
# STATE NAME NORMALIZATION
# --------------------------------------------------
STATE_MASTER = {
    "ANDHRA PRADESH": "Andhra Pradesh",
    "ARUNACHAL PRADESH": "Arunachal Pradesh",
    "ASSAM": "Assam",
    "BIHAR": "Bihar",
    "CHHATTISGARH": "Chhattisgarh",
    "DELHI": "NCT of Delhi",
    "GOA": "Goa",
    "GUJARAT": "Gujarat",
    "HARYANA": "Haryana",
    "HIMACHAL PRADESH": "Himachal Pradesh",
    "JHARKHAND": "Jharkhand",
    "KARNATAKA": "Karnataka",
    "KERALA": "Kerala",
    "MADHYA PRADESH": "Madhya Pradesh",
    "MAHARASHTRA": "Maharashtra",
    "ODISHA": "Odisha",
    "PUNJAB": "Punjab",
    "RAJASTHAN": "Rajasthan",
    "TAMIL NADU": "Tamil Nadu",
    "TELANGANA": "Telangana",
    "UTTAR PRADESH": "Uttar Pradesh",
    "UTTARAKHAND": "Uttarakhand",
    "WEST BENGAL": "West Bengal",
    "PUDUCHERRY": "Puducherry",
    "JAMMU AND KASHMIR": "Jammu and Kashmir",
    "LADAKH": "Ladakh",
    "CHANDIGARH": "Chandigarh",
    "ANDAMAN & NICOBAR ISLANDS": "Andaman and Nicobar Islands"
}

df["State_Map"] = df["State"].map(STATE_MASTER)

# --------------------------------------------------
# KPIs
# --------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Centers", df["Pincode"].nunique())
k2.metric("Poor Centers", (df["Quality_Flag"] == "POOR").sum())
k3.metric("States Covered", df["State"].nunique())
k4.metric("Avg FTA Proxy", round(df["FTA_Proxy_Rate"].mean(), 2))

st.markdown("---")

# --------------------------------------------------
# STATE SUMMARY FOR MAP
# --------------------------------------------------
state_summary = df.groupby("State_Map", as_index=False).agg(
    Total_Centers=("Pincode", "nunique"),
    Poor_Centers=("Quality_Flag", lambda x: (x == "POOR").sum()),
    Avg_FTA=("FTA_Proxy_Rate", "mean"),
    Biometric_Updates=("Biometric_Update_Total", "sum")
)

# --------------------------------------------------
# INDIA MAP (HOVER BASED)
# --------------------------------------------------
st.subheader("🗺️ National Aadhaar Quality Risk Map")

fig = px.choropleth(
    state_summary,
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/india_states.geojson",
    featureidkey="properties.ST_NM",
    locations="State_Map",
    color="Poor_Centers",
    color_continuous_scale=[
        "#e8f5e9",
        "#a5d6a7",
        "#66bb6a",
        "#43a047",
        "#ffb74d",
        "#ff7a00"
    ],
    hover_data={
        "Total_Centers": True,
        "Poor_Centers": True,
        "Avg_FTA": ":.2f",
        "Biometric_Updates": True
    }
)

fig.update_traces(
    hovertemplate="""
    <b>%{location}</b><br><br>
    Total Centers: %{customdata[0]}<br>
    Poor Centers: %{customdata[1]}<br>
    Avg FTA Proxy: %{customdata[2]:.2f}<br>
    Biometric Updates: %{customdata[3]}
    <extra></extra>
    """,
    marker_line_width=1.5,
    marker_line_color="#2f4f4f"
)

fig.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=0, b=0)
)

fig.update_geos(
    fitbounds="locations",
    visible=False
)

st.plotly_chart(fig, use_container_width=True)
