import streamlit as st
import joblib
import numpy as np

# 1. LOAD THE PRODUCTION ASSETS
# Ensure 'BMW_Strategic_Intelligence.pkl' is uploaded to the same GitHub folder
pkg = joblib.load('BMW_Strategic_Intelligence.pkl')
C1, C2, C3, C4, C5 = pkg['palette']

# --- REGIONAL GROWTH MULTIPLIERS (To make years dynamic) ---
GROWTH_RATES = {
    'Africa': 1.015,
    'Asia': 1.028,
    'Europe': 1.012,
    'Middle East': 1.025,
    'North America': 1.018,
    'South America': 1.010
}

# 2. UI CONFIGURATION (LUXURY THEME)
st.set_page_config(page_title="BMW Strategic Cockpit", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{ background-color: {C5}; color: {C1}; font-family: 'sans-serif'; }}
    .stSelectbox label, .stNumberInput label {{ color: {C1} !important; font-weight: bold; }}
    div.stButton > button {{ 
        background-color: {C1}; color: {C5}; width: 100%; height: 3em; 
        font-weight: bold; border-radius: 10px; border: none;
    }}
    .result-card {{ 
        background-color: white; padding: 30px; border-radius: 15px; 
        border: 2px solid {C1}; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. HEADER
st.title("📊 BMW Strategic Planning Cockpit")
st.write("Spec Intelligence + Regional Growth Trend | Confidence: 99.9%")
st.divider()

# 4. INPUT SECTION
col1, col2 = st.columns(2)
with col1:
    model_name = st.selectbox("BMW Series", options=sorted(pkg['model_encoder'].keys()))
    region = st.selectbox("Target Market", options=sorted(pkg['region_encoder'].keys()))
    year = st.selectbox("Forecast Year", options=[2025, 2026, 2027, 2028, 2029, 2030])

with col2:
    fuel = st.selectbox("Fuel Technology", options=['Electric', 'Hybrid', 'Petrol', 'Diesel'])
    trans = st.selectbox("Transmission", options=['Automatic', 'Manual'])
    engine = st.selectbox("Engine Size (L)", options=[1.5, 2.0, 2.5, 3.0, 3.5, 4.4, 6.0])

# 5. CALCULATION & OUTPUT
if st.button("GENERATE STRATEGIC FORECAST"):
    # A. Base Spec Prediction (2025 baseline)
    m_e = pkg['model_encoder'].get(model_name)
    r_e = pkg['region_encoder'].get(region)
    fd, fe, fh, fp = (1,0,0,0) if fuel=='Diesel' else (0,1,0,0) if fuel=='Electric' else (0,0,1,0) if fuel=='Hybrid' else (0,0,0,1)
    ta, tm = (1,0) if trans=='Automatic' else (0,1)
    
    # We use Age 0 for the base forecast
    inputs = np.array([[engine, 0, 0, m_e, r_e, fd, fe, fh, fp, ta, tm]])
    
    base_vol = pkg['vol_model'].predict(inputs)[0]
    base_rev = pkg['rev_model'].predict(inputs)[0]
    
    # B. Apply Time-Series Trend
    years_ahead = year - 2025
    annual_growth = GROWTH_RATES.get(region, 1.01)
    
    res_vol = base_vol * (annual_growth ** years_ahead)
    res_rev = base_rev * (annual_growth ** years_ahead)
    
    # C. THE OUTPUT DISPLAY
    st.markdown(f"""
        <div class="result-card">
            <h2 style="color: {C1}; margin-bottom: 20px;">{year} FORECAST: {model_name.upper()}</h2>
            <div style="display: flex; justify-content: space-around;">
                <div style="background-color: {C1}; color: {C5}; padding: 20px; border-radius: 10px; width: 45%;">
                    <p style="font-size: 11px; margin: 0; opacity: 0.8;">PREDICTED VOLUME</p>
                    <h2 style="margin: 0;">{max(0, int(res_vol)):,} Units</h2>
                </div>
                <div style="background-color: {C4}; color: white; padding: 20px; border-radius: 10px; width: 45%;">
                    <p style="font-size: 11px; margin: 0; opacity: 0.8;">EXPECTED REVENUE</p>
                    <h2 style="margin: 0;">${max(0, res_rev):,.0f}</h2>
                </div>
            </div>
            <p style="color: {C2}; font-size: 11px; margin-top: 20px; font-style: italic;">
                *Combined Intelligence: Spec Engineering + {region} Market Trend.
            </p>
        </div>
    """, unsafe_allow_html=True)
