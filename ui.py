import streamlit as st
import psutil
import GPUtil
import platform
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Set page configuration
st.set_page_config(
    page_title="Steampunk System Dashboard",
    page_icon="🪨",
    layout="wide",
)

# Custom CSS for enhanced steampunk theme
st.markdown(
    """
    <style>
    body {
        background: url('https://i.imgur.com/EkJoihO.jpg') no-repeat center center fixed;
        background-size: cover;
        color: #e3b23c;
        font-family: "Courier New", Courier, monospace;
    }

    .header-text {
        font-size: 3em;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
        color: #d4af37;
    }

    .steampunk-button {
        background-color: #704214;
        border: 3px solid #d4af37;
        border-radius: 50%;
        width: 150px;
        height: 150px;
        display: flex;
        justify-content: center;
        align-items: center;
        color: #ffffff;
        font-size: 1.2em;
        font-weight: bold;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        cursor: pointer;
        transition: transform 0.5s;
    }

    .steampunk-button:hover {
        background-color: #d4af37;
        color: #2c2f33;
        transform: rotate(360deg);
    }

    .system-data {
        background: rgba(0,0,0,0.7);
        border: 3px solid #d4af37;
        border-radius: 12px;
        padding: 20px;
        margin: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown("""
    <div class="header-text">
        Steampunk System Dashboard
    </div>
""", unsafe_allow_html=True)

# Load AI Model
model_name = "meta-llama/Llama-2-7b-chat-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, device_map="auto", torch_dtype=torch.float16, offload_buffers=True
)

# Fetch system information
def get_system_info():
    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Processor": platform.processor(),
        "System Name": platform.node(),
        "CPU Usage (%)": psutil.cpu_percent(interval=1),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Cores": psutil.cpu_count(logical=True),
        "Total Memory (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),
        "Available Memory (GB)": round(psutil.virtual_memory().available / (1024 ** 3), 2),
        "Memory Usage (%)": psutil.virtual_memory().percent,
        "Total Disk Space (GB)": round(psutil.disk_usage('/').total / (1024 ** 3), 2),
        "Free Disk Space (GB)": round(psutil.disk_usage('/').free / (1024 ** 3), 2),
        "Disk Usage (%)": psutil.disk_usage('/').percent,
        "Battery Percentage (%)": psutil.sensors_battery().percent if psutil.sensors_battery() else "N/A",
        "Battery Charging": psutil.sensors_battery().power_plugged if psutil.sensors_battery() else "N/A",
        "Network Sent (MB)": round(psutil.net_io_counters().bytes_sent / (1024 ** 2), 2),
        "Network Received (MB)": round(psutil.net_io_counters().bytes_recv / (1024 ** 2), 2),
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        system_info.update({
            "GPU Name": gpu.name,
            "GPU Memory Total (GB)": round(gpu.memoryTotal / 1024, 2),
            "GPU Memory Used (GB)": round(gpu.memoryUsed / 1024, 2),
            "GPU Memory Usage (%)": gpu.memoryUtil * 100,
            "GPU Temperature (C)": gpu.temperature,
        })
    else:
        system_info["GPU"] = "No GPU detected"

    return system_info

# Create gauge chart
def create_gauge_chart(value, title, max_value=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "#d4af37"},
            'bgcolor': "#2c2f33",
            'borderwidth': 2,
            'bordercolor': "#704214",
            'steps': [
                {'range': [0, max_value * 0.5], 'color': "#2c2f33"},
                {'range': [max_value * 0.5, max_value], 'color': "#704214"}
            ]
        }
    ))
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="#000000",
        font=dict(color="#e3b23c")
    )
    return fig

# Display system data
info = get_system_info()

st.markdown(f"""
    <div class="system-data">
        <h3>System Information:</h3>
        <p><strong>OS:</strong> {info['OS']} ({info['OS Version']})</p>
        <p><strong>Processor:</strong> {info['Processor']}</p>
        <p><strong>System Name:</strong> {info['System Name']}</p>
        <p><strong>Battery Percentage:</strong> {info['Battery Percentage (%)']}</p>
        <p><strong>Battery Charging:</strong> {info['Battery Charging']}</p>
        <p><strong>Network Sent:</strong> {info['Network Sent (MB)']} MB</p>
        <p><strong>Network Received:</strong> {info['Network Received (MB)']} MB</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.plotly_chart(create_gauge_chart(info['CPU Usage (%)'], "CPU Usage (%)"), use_container_width=True)

with col2:
    st.plotly_chart(create_gauge_chart(info['Memory Usage (%)'], "Memory Usage (%)"), use_container_width=True)

with col3:
    if 'GPU Memory Usage (%)' in info:
        st.plotly_chart(create_gauge_chart(info['GPU Memory Usage (%)'], "GPU Usage (%)"), use_container_width=True)
    else:
        st.text("No GPU detected.")

with col4:
    st.plotly_chart(create_gauge_chart(info['Disk Usage (%)'], "Disk Usage (%)"), use_container_width=True)

with col5:
    st.plotly_chart(create_gauge_chart(info['Network Sent (MB)'], "Net Sent (MB)", max_value=1000), use_container_width=True)

with col6:
    st.plotly_chart(create_gauge_chart(info['Network Received (MB)'], "Net Received (MB)", max_value=1000), use_container_width=True)

# Interactive button
if st.button("Spin Gear"):
    st.write("Gear spinning... Data refreshed!")
    st.experimental_rerun()
