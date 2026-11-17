import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Galamsey River Simulation", page_icon="🌊", layout="wide")

# --- CUSTOM CSS: HIGH CONTRAST TEXT & WHITE BACKGROUND ---
st.markdown("""
<style>
    /* Main Content Background set to Clean White */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    /* Sidebar Styling with Dark, High-Contrast Text */
    [data-testid="stSidebar"] {
        background-color: #f0f4f8;
        border-right: 1px solid #d1d9e0;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {
        color: #0b2545 !important;
        font-weight: 600 !important;
    }

    /* Floating Animated Header */
    @keyframes floatAnimation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-4px); }
        100% { transform: translateY(0px); }
    }
    
    .animated-header {
        animation: floatAnimation 3s ease-in-out infinite;
        font-size: 2.3rem;
        font-weight: 800;
        color: #0b2545;
        margin-bottom: 0px;
    }

    /* Make Sliders Moderately Larger */
    [data-baseweb="slider"] {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stSlider div[data-baseweb="slider"] div[role="slider"] {
        width: 22px;
        height: 22px;
        background-color: #134074;
    }

    /* Styled Metric Cards */
    .metric-card {
        background: #f8f9fa;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #134074;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown('<p class="animated-header">🌊 Galamsey River Pollution & pH Simulation Engine</p>', unsafe_allow_html=True)
st.markdown("Interactive hydrological modeling dashboard tracking acid mine drainage downstream with customizable parameters.")
st.write("")

# --- EXPANDED SIDEBAR SLIDERS ---
st.sidebar.header("🎛️ Simulation Parameters")

st.sidebar.subheader("Mining & Weather")
mining_severity = st.sidebar.slider("Mining Intensity Level", 0.5, 2.5, 1.2, 0.1, help="Simulates acid mine runoff severity.")
base_rainfall = st.sidebar.slider("Base Rainfall (mm/day)", 0.0, 20.0, 6.0, 0.5, help="Rainfall volume diluting acidity.")
simulation_days = st.sidebar.slider("Simulation Duration (Days)", 7, 90, 30, 1)

st.sidebar.subheader("River Hydrology & Sensors")
num_stations = st.sidebar.slider("Downstream Stations", 2, 6, 4, 1, help="Number of monitoring posts along the river.")
station_distance = st.sidebar.slider("Distance Between Stations (km)", 1.0, 5.0, 2.5, 0.5)
river_buffering = st.sidebar.slider("River Natural Alkalinity (pH)", 6.5, 8.0, 7.2, 0.1, help="Natural baseline pH of unpolluted water.")
sensor_noise = st.sidebar.slider("Sensor Noise Variance", 0.0, 0.3, 0.1, 0.05, help="Simulates environmental reading variance.")

# --- SIMULATION ENGINE ---
np.random.seed(42)
stations = [f"Station {i+1} ({i*station_distance:.1f} km)" for i in range(num_stations)]
distances = np.array([i * station_distance for i in range(num_stations)])
rainfall_mm = np.random.exponential(scale=base_rainfall, size=simulation_days)

simulation_records = []
for day in range(simulation_days):
    rain = rainfall_mm[day]
    mining_activity = mining_severity * np.random.uniform(0.8, 1.2)
    
    for i, station in enumerate(stations):
        dist = distances[i]
        pollution_impact = (4.5 * mining_activity) / (1.0 + 0.25 * dist)
        dilution_factor = min(2.0, rain * 0.12)
        
        simulated_ph = river_buffering - max(0, pollution_impact - dilution_factor)
        simulated_ph += np.random.normal(0, sensor_noise)
        simulated_ph = np.clip(simulated_ph, 3.0, 8.5)
        
        status = 'Critical' if simulated_ph < 5.5 else ('Warning' if simulated_ph < 6.5 else 'Safe')
        simulation_records.append({
            'Day': day + 1,
            'Station': station,
            'Distance_km': dist,
            'Rainfall_mm': round(rain, 1),
            'Simulated_pH': round(simulated_ph, 2),
            'Status': status
        })

df = pd.DataFrame(simulation_records)

# --- QUICK METRICS ROW ---
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-weight:600; color:#0b2545;">Total Data Points</p>
        <h2 style="margin:0; color:#134074;">{len(df)}</h2>
    </div>
    """, unsafe_allow_html=True)
with col2:
    critical_count = len(df[df['Status'] == 'Critical'])
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-weight:600; color:#0b2545;">Critical pH Events (&lt;5.5)</p>
        <h2 style="margin:0; color: #d9534f;">{critical_count}</h2>
    </div>
    """, unsafe_allow_html=True)
with col3:
    avg_ph = df['Simulated_pH'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <p style="margin:0; font-weight:600; color:#0b2545;">Basin Average pH</p>
        <h2 style="margin:0; color:#134074;">{avg_ph:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- PLOTTING RESULTS ---
st.subheader("📈 Downstream pH Trends Over Time")
fig, ax = plt.subplots(figsize=(10, 4.5))
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

colors = ['#d9534f', '#f0ad4e', '#134074', '#00acc1', '#5cb85c', '#8e44ad']
for i, station in enumerate(df['Station'].unique()):
    station_data = df[df['Station'] == station]
    ax.plot(station_data['Day'], station_data['Simulated_pH'], 
            label=station, color=colors[i % len(colors)], linewidth=2.2, marker='o', markersize=3)

ax.axhline(y=6.5, color='#e74c3c', linestyle='--', linewidth=1.5, label='WHO Safe Threshold (pH 6.5)')
ax.set_xlabel('Simulation Day', fontsize=11, fontweight='bold', color='#0b2545')
ax.set_ylabel('Simulated pH Level', fontsize=11, fontweight='bold', color='#0b2545')
ax.set_ylim(3.0, 9.0)
ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True, facecolor='white')
ax.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

st.pyplot(fig)

# --- FILTERABLE DATA TABLE ---
st.subheader("📋 Simulation Logs & Status Table")
status_filter = st.selectbox("Filter Table by Water Status", ["All", "Critical", "Warning", "Safe"])
filtered_df = df if status_filter == "All" else df[df['Status'] == status_filter]

st.dataframe(filtered_df, use_container_width=True)