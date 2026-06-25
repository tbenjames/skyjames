"""
SkyJames - Business Intelligence Dashboard
Fixed: Removed use_column_width from buttons
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import numpy as np
import os

st.set_page_config(page_title="SkyJames BI", layout="wide")

st.title("📊 SkyJames Business Intelligence")

# ==================== SESSION STATE ====================
if 'export_data' not in st.session_state:
    st.session_state.export_data = None
if 'notification' not in st.session_state:
    st.session_state.notification = ""

def notify(msg):
    st.session_state.notification = msg

# ==================== GENERATE SAMPLE DATA ====================
def generate_sample_data():
    """Generate sample data for BI dashboard"""
    dates = pd.date_range(end=datetime.now(), periods=30)
    np.random.seed(42)
    
    return {
        'daily': pd.DataFrame({
            'Date': dates,
            'Videos': np.random.randint(50, 200, 30),
            'Detections': np.random.randint(200, 800, 30),
            'Accuracy': np.clip(0.85 + np.random.randn(30) * 0.03, 0.80, 0.98)
        }),
        'models': pd.DataFrame({
            'Model': ['YOLO11', 'YOLO11-seg', 'YOLO11-pose', 'YOLO11-obb'],
            'Speed': [26.7, 18.2, 15.4, 12.1],
            'Accuracy': [94.2, 92.1, 89.7, 87.3]
        }),
        'geo': pd.DataFrame({
            'Country': ['USA', 'UK', 'Germany', 'France', 'Japan', 'Australia', 'Canada'],
            'Videos': np.random.randint(50, 300, 7),
            'Detections': np.random.randint(200, 1000, 7)
        })
    }

# Load data
data = generate_sample_data()

# ==================== CSS ====================
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid #e8e8e8;
        text-align: center;
    }
    .metric-card .value {
        font-size: 2em;
        font-weight: 700;
        color: #1a1a2e;
    }
    .metric-card .label {
        color: #888;
        font-size: 0.9em;
    }
    .metric-card .change {
        font-size: 0.8em;
        color: #34c759;
    }
    .metric-card .change.negative {
        color: #ff3b30;
    }
    .stButton > button {
        width: 100% !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
    }
    .stButton > button[kind="primary"] {
        background: #4a6cf7 !important;
        color: white !important;
    }
    .notification {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
        background: #e8f5e9;
        border-left: 4px solid #34c759;
    }
    .notification.error {
        background: #fbe9e7;
        border-left-color: #ff3b30;
    }
</style>
""", unsafe_allow_html=True)

# ==================== NOTIFICATION ====================
if st.session_state.notification:
    cls = "notification"
    if "❌" in st.session_state.notification:
        cls += " error"
    st.markdown(f'<div class="{cls}">{st.session_state.notification}</div>', unsafe_allow_html=True)
    st.session_state.notification = ""

# ==================== KPI CARDS ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">1,247</div>
        <div class="label">Total Videos Processed</div>
        <div class="change">+12.3%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">12,456</div>
        <div class="label">Total Detections</div>
        <div class="change">+8.7%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">42ms</div>
        <div class="label">Avg Processing Time</div>
        <div class="change">-5.2%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="value">94.2%</div>
        <div class="label">Detection Accuracy</div>
        <div class="change">+2.1%</div>
    </div>
    """, unsafe_allow_html=True)

# ==================== TRENDS ====================
st.markdown("---")
st.subheader("📈 Performance Trends")

col1, col2 = st.columns(2)

with col1:
    fig = px.line(
        data['daily'], 
        x='Date', 
        y=['Videos', 'Detections'], 
        title="Daily Activity"
    )
    fig.update_layout(showlegend=True, height=400)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    fig = px.line(
        data['daily'], 
        x='Date', 
        y='Accuracy', 
        title="Detection Accuracy Trend"
    )
    fig.add_hline(y=0.90, line_dash="dash", line_color="red", annotation_text="Target: 90%")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_column_width=True)

# ==================== MODEL PERFORMANCE ====================
st.markdown("---")
st.subheader("🤖 Model Performance")

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        data['models'], 
        x='Model', 
        y='Speed', 
        title="Model Speed (FPS)",
        color='Speed',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_column_width=True)

with col2:
    fig = px.bar(
        data['models'], 
        x='Model', 
        y='Accuracy', 
        title="Model Accuracy (%)",
        color='Accuracy',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_column_width=True)

# ==================== GEOGRAPHIC DISTRIBUTION ====================
st.markdown("---")
st.subheader("🌍 Geographic Activity")

fig = px.choropleth(
    data['geo'],
    locations='Country',
    locationmode='country names',
    color='Videos',
    title="Videos Processed by Country",
    color_continuous_scale='Viridis'
)
fig.update_layout(height=400)
st.plotly_chart(fig, use_column_width=True)

# ==================== EXPORT OPTIONS ====================
st.markdown("---")
st.subheader("📤 Export Reports")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export as CSV", type="primary"):
        try:
            # Combine all data
            combined_data = pd.concat([
                data['daily'].assign(Source='Daily'),
                data['models'].assign(Source='Models'),
                data['geo'].assign(Source='Geographic')
            ])
            csv = combined_data.to_csv(index=False)
            
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"skyjames_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            notify("✅ CSV report generated!")
        except Exception as e:
            notify(f"❌ Error generating CSV: {e}")

with col2:
    if st.button("📈 Export as JSON", type="primary"):
        try:
            json_data = {
                'daily': data['daily'].to_dict(orient='records'),
                'models': data['models'].to_dict(orient='records'),
                'geo': data['geo'].to_dict(orient='records'),
                'timestamp': datetime.now().isoformat()
            }
            json_str = json.dumps(json_data, indent=2)
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_str,
                file_name=f"skyjames_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            notify("✅ JSON report generated!")
        except Exception as e:
            notify(f"❌ Error generating JSON: {e}")

with col3:
    if st.button("📄 Generate PDF Report", type="primary"):
        try:
            # Create a simple HTML report
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SkyJames Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #1a1a2e; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #4a6cf7; color: white; }}
                    .metric {{ display: inline-block; margin: 20px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                </style>
            </head>
            <body>
                <h1>🚀 SkyJames Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Summary</h2>
                <div class="metric">Total Videos: 1,247</div>
                <div class="metric">Total Detections: 12,456</div>
                <div class="metric">Accuracy: 94.2%</div>
                
                <h2>Daily Activity</h2>
                {data['daily'].to_html()}
                
                <h2>Model Performance</h2>
                {data['models'].to_html()}
                
                <p style="color: #888; margin-top: 40px;">Generated by SkyJames BI Dashboard</p>
            </body>
            </html>
            """
            
            st.download_button(
                label="⬇️ Download HTML Report",
                data=html_content,
                file_name=f"skyjames_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )
            notify("✅ HTML report generated!")
        except Exception as e:
            notify(f"❌ Error generating report: {e}")

# ==================== EXPORT ALL DATA ====================
st.markdown("---")
st.subheader("📊 Export All Data")

if st.button("📦 Export Complete Dataset", type="primary"):
    try:
        # Create comprehensive export
        export_data = {
            'daily_activity': data['daily'].to_dict(orient='records'),
            'model_performance': data['models'].to_dict(orient='records'),
            'geographic_distribution': data['geo'].to_dict(orient='records'),
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'version': '2.0.0',
                'source': 'SkyJames BI Dashboard'
            }
        }
        
        json_str = json.dumps(export_data, indent=2)
        
        st.download_button(
            label="⬇️ Download Complete Dataset (JSON)",
            data=json_str,
            file_name=f"skyjames_complete_export_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )
        notify("✅ Complete dataset exported!")
    except Exception as e:
        notify(f"❌ Error exporting dataset: {e}")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #999; padding: 20px 0;">
    <p>🚀 SkyJames BI Dashboard • Updated in real-time</p>
    <p style="font-size: 0.8em;">Click export buttons above to download reports</p>
</div>
""", unsafe_allow_html=True)
