"""
SkyJames - 3D Visualization Dashboard (Fixed)
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import time

def create_3d_scene(data):
    """Create interactive 3D scene"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter3d(
        x=data['x'],
        y=data['y'],
        z=data['z'],
        mode='markers',
        marker=dict(
            size=data.get('size', 5),
            color=data.get('color', 'blue'),
            colorscale='Viridis',
            opacity=0.8,
            colorbar=dict(title="Intensity")
        )
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis_title='X Position',
            yaxis_title='Y Position',
            zaxis_title='Z Position',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        title="3D Detection Visualization",
        height=600
    )
    
    return fig

def create_heatmap(data):
    """Create heatmap of detection activity"""
    fig = go.Figure(data=go.Heatmap(
        z=data['activity'],
        x=data['x_labels'],
        y=data['y_labels'],
        colorscale='Viridis'
    ))
    
    fig.update_layout(
        title="Detection Activity Heatmap",
        height=500
    )
    
    return fig

def main():
    st.title("🌐 3D Visualization Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["3D Scene", "Heatmap", "Real-time"])
    
    with tab1:
        st.subheader("3D Detection Visualization")
        np.random.seed(42)
        data = {
            'x': np.random.randn(100) * 10,
            'y': np.random.randn(100) * 10,
            'z': np.random.randn(100) * 5 + 5,
            'size': np.random.randint(5, 20, 100),
            'color': np.random.rand(100)
        }
        
        fig = create_3d_scene(data)
        st.plotly_chart(fig, use_column_width=True)
    
    with tab2:
        st.subheader("Activity Heatmap")
        heatmap_data = {
            'activity': np.random.rand(20, 20),
            'x_labels': [f'X{i}' for i in range(20)],
            'y_labels': [f'Y{i}' for i in range(20)]
        }
        fig = create_heatmap(heatmap_data)
        st.plotly_chart(fig, use_column_width=True)
    
    with tab3:
        st.subheader("Real-time 3D Visualization")
        st.info("Connect to WebSocket for real-time 3D updates")
        
        # Removed use_column_width from button
        if st.button("Start Real-time Stream"):
            placeholder = st.empty()
            for i in range(20):
                new_data = {
                    'x': np.random.randn(100) * 10,
                    'y': np.random.randn(100) * 10,
                    'z': np.random.randn(100) * 5 + 5,
                    'size': np.random.randint(5, 20, 100),
                    'color': np.random.rand(100)
                }
                fig = create_3d_scene(new_data)
                placeholder.plotly_chart(fig, use_column_width=True)
                time.sleep(0.5)

if __name__ == "__main__":
    main()
