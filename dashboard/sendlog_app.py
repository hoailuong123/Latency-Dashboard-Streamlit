import streamlit as st
import requests
import uuid
import random
import os
import pandas as pd

# Remove proxy
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(proxy_var, None)

# Page configuration
st.set_page_config(
    page_title="Send Logs - On-device Latency",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.header("Send Logs App")

# Main title
st.title("Send Latency Logs")

st.info("Send logs directly to the backend and automatically save to CSV")

# Two columns for single log and batch log
col1, col2 = st.columns(2)

# Shared log file path
SHARED_LOG = "/app/latency_logs.csv"

# Load latency data for send log
def load_latency_for_sendlog():
    if os.path.exists(SHARED_LOG):
        st.info(f"Using shared latency file: {SHARED_LOG}")
        return pd.read_csv(SHARED_LOG)
    uploaded = st.file_uploader("Upload latency CSV", type=["csv"])
    if uploaded is not None:
        return pd.read_csv(uploaded)
    st.warning("No latency data available.")
    return None

# Load latency data
df = load_latency_for_sendlog()

# ============================================================
# SINGLE LOG SECTION
# ============================================================
with col1:
    st.subheader("Send Single Log")
    
    with st.form("single_log_form"):
        request_id = st.text_input(
            "Request ID",
            value=f"req_{uuid.uuid4().hex[:8]}",
            help="Unique identifier for this request"
        )
        
        model_name = st.selectbox(
            "Model Name",
            ["LFM2-V1-6B", "LFM2-VL-450M", "GPT-2", "BERT-Base", "Other"],
            help="Select the model used"
        )
        
        if model_name == "Other":
            model_name = st.text_input("Enter model name:")
        
        latency_ms = st.number_input(
            "Latency (ms)",
            min_value=0.0,
            value=200.0,
            step=0.1,
            help="Latency in milliseconds"
        )
        
        device_model = st.selectbox(
            "Device Model",
            ["iPhone 13", "iPhone 14", "iPhone 15 Pro", "iPhone SE", "Other"],
            help="Select the device model"
        )
        
        if device_model == "Other":
            device_model = st.text_input("Enter device model:")
        
        app_version = st.selectbox(
            "App Version",
            ["1.0.0", "1.1.0", "2.0.0", "0.1.0", "Other"],
            help="Select the app version"
        )
        
        if app_version == "Other":
            app_version = st.text_input("Enter app version:")

        # --- Extended logging fields ---
        st.markdown("### 📎 Additional Context")

        col_ext1, col_ext2 = st.columns(2)
        with col_ext1:
            user_feedback_display = st.radio(
                "User Feedback",
                options=["None", "Thumbs Up", "Thumbs Down"],
                index=0,
                help="Collect real-world user feedback"
            )
        with col_ext2:
            device_temperature = st.number_input(
                "Device Temperature (°C)",
                min_value=0.0,
                max_value=100.0,
                value=35.0,
                step=0.1,
                help="Device temperature at runtime (optional)"
            )

        battery_percentage = st.slider(
            "Battery Percentage (%)",
            min_value=0,
            max_value=100,
            value=80,
            help="Battery level when the request was made (optional)"
        )

        crashed = st.checkbox(
            "This request caused a crash",
            value=False,
            help="Check if the app/session crashed"
        )
        crash_log = ""
        if crashed:
            crash_log = st.text_area(
                "Crash Log / Error Message",
                help="Paste crash stacktrace or error message to improve runtime compatibility",
                height=120,
            )

        submit_single = st.form_submit_button("Send Log", use_container_width=True)
    
    if submit_single:
        log_data = {
            "request_id": request_id,
            "model_name": model_name,
            "latency_ms": latency_ms,
            "device_model": device_model,
            "app_version": app_version,
            "crash_log": crash_log if crash_log else None,
            "user_feedback": (
                "up" if user_feedback_display == "👍 Thumbs Up"
                else "down" if user_feedback_display == "👎 Thumbs Down"
                else None
            ),
            "device_temperature": device_temperature,
            "battery_percentage": float(battery_percentage),
        }
        
        try:
            response = requests.post(
                "http://localhost:8000/api/logs",
                json=log_data,
                timeout=5
            )
            
            if response.status_code == 200:
                st.success("✅ Log sent successfully!")
                st.json(response.json())
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            st.info("Make sure backend is running: `python -m uvicorn backend:app --host 0.0.0.0 --port 8000`")

# ============================================================
# BATCH LOG SECTION
# ============================================================
with col2:
    st.subheader("Send Batch Logs")
    
    num_logs = st.number_input(
        "Number of logs",
        min_value=1,
        max_value=100,
        value=5,
        help="How many logs to generate and send"
    )
    
    batch_model = st.selectbox(
        "Model Name (Batch)",
        ["LFM2-V1-6B", "LFM2-VL-450M", "GPT-2", "BERT-Base"],
        key="batch_model"
    )
    
    batch_device = st.selectbox(
        "Device Model (Batch)",
        ["iPhone 13", "iPhone 14", "iPhone 15 Pro", "iPhone SE"],
        key="batch_device"
    )
    
    batch_version = st.selectbox(
        "App Version (Batch)",
        ["1.0.0", "1.1.0", "2.0.0", "0.1.0"],
        key="batch_version"
    )
    
    batch_latency_min = st.number_input(
        "Min Latency (ms)",
        min_value=0.0,
        value=100.0,
        step=0.1
    )
    
    batch_latency_max = st.number_input(
        "Max Latency (ms)",
        min_value=0.0,
        value=300.0,
        step=0.1
    )
    
    if st.button(" Send Batch Logs", use_container_width=True, key="batch_submit"):
        logs = []
        for i in range(num_logs):
            log = {
                "request_id": f"req_{uuid.uuid4().hex[:8]}",
                "model_name": batch_model,
                "latency_ms": round(random.uniform(batch_latency_min, batch_latency_max), 1),
                "device_model": batch_device,
                "app_version": batch_version
            }
            logs.append(log)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/logs/batch",
                json=logs,
                timeout=10
            )
            
            if response.status_code == 200:
                st.success(f"✅ {num_logs} logs sent successfully!")
                st.json(response.json())
            else:
                st.error(f"❌ Error: {response.status_code}")
                st.json(response.json())
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
            st.info("Make sure backend is running: `python -m uvicorn backend:app --host 0.0.0.0 --port 8000`")

# ============================================================
# STATISTICS SECTION
# ============================================================
st.divider()

st.subheader("Backend Statistics & Management")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(" Get Statistics", use_container_width=True):
        try:
            response = requests.get("http://localhost:8000/api/stats", timeout=5)
            if response.status_code == 200:
                stats = response.json()
                st.metric("Total Records", stats['total_records'])
                st.metric("Average Latency (ms)", f"{stats['avg_latency_ms']:.2f}")
            else:
                st.error("Failed to get statistics")
        except Exception as e:
            st.error(f"Connection error: {e}")

with col2:
    if st.button("Get Log Count", use_container_width=True):
        try:
            response = requests.get("http://localhost:8000/api/logs/count", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.metric("Total Logs", data['total_logs'])
            else:
                st.error("Failed to get count")
        except Exception as e:
            st.error(f"Connection error: {e}")

with col3:
    if st.button("Clear All Logs", use_container_width=True):
        try:
            response = requests.delete("http://localhost:8000/api/logs/clear", timeout=5)
            if response.status_code == 200:
                st.success("✅ All logs cleared!")
                st.json(response.json())
            else:
                st.error("Failed to clear logs")
        except Exception as e:
            st.error(f"Connection error: {e}")

# Footer
st.divider()

