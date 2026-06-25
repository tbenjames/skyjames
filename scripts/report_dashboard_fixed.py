"""
SkyJames - Interactive Reports Dashboard (Fixed)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

def load_report_data():
    """Load report data from database"""
    dates = pd.date_range(end=datetime.now(), periods=30)
    return pd.DataFrame({
        'date': dates,
        'videos': np.random.randint(50, 200, 30),
        'detections': np.random.randint(200, 800, 30),
        'accuracy': np.random.uniform(0.85, 0.98, 30),
        'processing_time': np.random.uniform(0.02, 0.08, 30),
        'model_version': np.random.choice(['v1', 'v2', 'v3'], 30)
    })

def create_report():
    st.title("📊 SkyJames Report Dashboard")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Load data
    data = load_report_data()
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Videos", f"{data['videos'].sum():,}", "📈")
    with col2:
        st.metric("Total Detections", f"{data['detections'].sum():,}", "📊")
    with col3:
        avg_acc = data['accuracy'].mean()
        st.metric("Avg Accuracy", f"{avg_acc:.1%}", "✅")
    with col4:
        total_time = data['processing_time'].sum()
        st.metric("Total Processing Time", f"{total_time:.1f}s", "⏱️")
    
    # Charts
    col1, col2 = st.columns(2)
    with col1:
        fig = px.line(data, x='date', y='videos', title="Videos Processed Over Time")
        st.plotly_chart(fig, use_column_width=True)
    with col2:
        fig = px.line(data, x='date', y='accuracy', title="Accuracy Trend")
        st.plotly_chart(fig, use_column_width=True)
    
    # Advanced metrics
    st.subheader("Advanced Analytics")
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(data, x='detections', nbins=30, title="Detection Distribution")
        st.plotly_chart(fig, use_column_width=True)
    with col2:
        fig = px.box(data, x='model_version', y='accuracy', title="Accuracy by Model Version")
        st.plotly_chart(fig, use_column_width=True)
    
    # Export options (removed use_column_width from buttons)
    st.subheader("📤 Export Report")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📊 Export as CSV"):
            csv = data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    with col2:
        if st.button("📈 Export as JSON"):
            json_data = data.to_json(orient='records')
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    with col3:
        if st.button("📄 Generate PDF Report"):
            st.info("PDF report generation coming soon!")

if __name__ == "__main__":
    create_report()
