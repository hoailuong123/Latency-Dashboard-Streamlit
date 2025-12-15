import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

SHARED_LOG = "/app/latency_logs.csv"

def load_latency():
    # Always use the shared volume file; do not prompt user to upload
    if os.path.exists(SHARED_LOG):
        st.info(f"Loading latency data from shared volume: {SHARED_LOG}")
        try:
            return pd.read_csv(SHARED_LOG)
        except Exception as e:
            st.error(f"Failed to read {SHARED_LOG}: {e}")
            return None
    st.warning(f"No latency data available at {SHARED_LOG}")
    return None

# Remove proxy
for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']:
    os.environ.pop(proxy_var, None)


# Page configuration
st.set_page_config(
    page_title="On-device Latency Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .metric-card {
            background-color: #1f1f2e;
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #00d4ff;
        }
        .metric-label {
            font-size: 0.9em;
            color: #888;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for filters
st.sidebar.header("🔧 Filters")

# Always load from shared file (no uploader)
df = load_latency()

if df is not None:
    # Display data info
    st.sidebar.success(f"✅ File loaded! ({len(df)} rows)")
    
    # Data source info (show path)
    st.markdown(f"**Data source:** {SHARED_LOG}")
    
    # Get unique values for filters
    model_names = sorted(df['model_name'].unique()) if 'model_name' in df.columns else []
    device_models = sorted(df['device_model'].unique()) if 'device_model' in df.columns else []
    app_versions = sorted(df['app_version'].unique()) if 'app_version' in df.columns else []
    feedback_values = sorted([v for v in df['user_feedback'].dropna().unique()]) if 'user_feedback' in df.columns else []
    
    # Filters
    st.sidebar.subheader("Model name")
    selected_models = st.sidebar.multiselect(
        "Select models",
        options=model_names,
        default=model_names[:2] if len(model_names) > 0 else [],
        key="model_filter"
    )
    
    st.sidebar.subheader("Device model")
    selected_devices = st.sidebar.multiselect(
        "Select devices",
        options=device_models,
        default=device_models if len(device_models) > 0 else [],
        key="device_filter"
    )
    
    st.sidebar.subheader("App version")
    selected_versions = st.sidebar.multiselect(
        "Select app versions",
        options=app_versions,
        default=app_versions if len(app_versions) > 0 else [],
        key="version_filter"
    )
    
    # Extended filters (optional columns)
    if 'user_feedback' in df.columns and feedback_values:
        st.sidebar.subheader("User feedback")
        selected_feedback = st.sidebar.multiselect(
            "Select feedback",
            options=feedback_values,
            default=feedback_values,
            key="feedback_filter"
        )
    else:
        selected_feedback = []

    only_crashed = False
    if 'crash_log' in df.columns:
        only_crashed = st.sidebar.checkbox(
            "Only crashed sessions",
            value=False
        )

    if 'device_temperature' in df.columns:
        st.sidebar.subheader("Device temperature")
        temp_levels = ["nominal", "fair", "serious", "critical"]

        # Lấy các giá trị thực tế xuất hiện
        existing = sorted(df['device_temperature'].dropna().unique())

        selected_temps = st.sidebar.multiselect(
            "Select temperature levels",
            options=existing,
            default=existing
        )
    else:
        selected_temps = []



    batt_min = batt_max = None
    if 'battery_percentage' in df.columns:
        st.sidebar.subheader("Battery level (%)")
        batt_min_val = float(df['battery_percentage'].min())
        batt_max_val = float(df['battery_percentage'].max())
        batt_min, batt_max = st.sidebar.slider(
            "Battery range",
            min_value=float(batt_min_val),
            max_value=float(batt_max_val),
            value=(float(batt_min_val), float(batt_max_val))
        )

    # Filter dataframe
    filtered_df = df[
        (df['model_name'].isin(selected_models)) &
        (df['device_model'].isin(selected_devices)) &
        (df['app_version'].isin(selected_versions))
    ]

    if 'user_feedback' in filtered_df.columns and selected_feedback:
        filtered_df = filtered_df[filtered_df['user_feedback'].isin(selected_feedback)]

    if 'crash_log' in filtered_df.columns and only_crashed:
        filtered_df = filtered_df[filtered_df['crash_log'].notna() & (filtered_df['crash_log'] != "")]

    if selected_temps:
        filtered_df = filtered_df[filtered_df["device_temperature"].isin(selected_temps)]


    if 'battery_percentage' in filtered_df.columns and batt_min is not None and batt_max is not None:
        filtered_df = filtered_df[
            (filtered_df['battery_percentage'] >= batt_min) &
            (filtered_df['battery_percentage'] <= batt_max)
        ]
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📌 Per-Run Analysis", "🆚 Compare Runs"])
    with tab1:
    
    # Main content
        st.title("📊 On-device Latency Dashboard")
    
    # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_latency = filtered_df['latency_ms'].mean() if 'latency_ms' in filtered_df.columns else 0
            st.metric("Avg latency (ms)", f"{avg_latency:.1f}")
        
        with col2:
            min_latency = filtered_df['latency_ms'].min() if 'latency_ms' in filtered_df.columns else 0
            st.metric("Min latency (ms)", f"{min_latency:.1f}")
        
        with col3:
            max_latency = filtered_df['latency_ms'].max() if 'latency_ms' in filtered_df.columns else 0
            st.metric("Max latency (ms)", f"{max_latency:.1f}")
        
        with col4:
            if 'latency_ms' in filtered_df.columns:
                p95_latency = filtered_df['latency_ms'].quantile(0.95)
                st.metric("P95 latency (ms)", f"{p95_latency:.1f}")

    # Extended metrics row
        ext1, ext2, ext3, ext4 = st.columns(4)
        with ext1:
            if 'crash_log' in filtered_df.columns and len(filtered_df) > 0:
                crash_rate = (filtered_df['crash_log'].notna() & (filtered_df['crash_log'] != "")).mean() * 100
                st.metric("Crash rate (%)", f"{crash_rate:.1f}")
        with ext2:
            if 'user_feedback' in filtered_df.columns and len(filtered_df) > 0:
                up_rate = (filtered_df['user_feedback'] == "up").mean() * 100
                st.metric("👍 Positive feedback (%)", f"{up_rate:.1f}")
        with ext3:
            if 'device_temperature' in filtered_df.columns and len(filtered_df) > 0:
                most_common_temp = filtered_df['device_temperature'].mode().iloc[0]
                st.metric("Most common temperature", most_common_temp)

        with ext4:
            if 'battery_percentage' in filtered_df.columns and len(filtered_df) > 0:
                avg_batt = filtered_df['battery_percentage'].mean()
                st.metric("Avg battery (%)", f"{avg_batt:.1f}")
            
        st.subheader("📌 Model Summary Table")

        summary_df = filtered_df.groupby("model_name").agg({
                    "latency_ms": ["mean", "min", "max", lambda x: x.quantile(0.95)],
                    "device_temperature": lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None,
                    "battery_percentage": "mean",
                    "crash_log": lambda x: (x.notna() & (x != "")).mean() * 100,
                    "user_feedback": lambda x: (x=="up").mean() * 100
                })

        summary_df.columns = [
                        "Avg Latency", "Min Latency", "Max Latency", "P95 Latency",
                        "Avg Temp", "Avg Battery", "Crash %", "Positive Feedback %"
                    ]

        st.dataframe(summary_df, use_container_width=True)  
        
        # Charts section
        st.subheader("📈 Latency over time")
        
        if 'request_id' in filtered_df.columns and 'latency_ms' in filtered_df.columns:
            # Latency over time chart
            fig_time = go.Figure()
            
            for model in selected_models:
                model_data = filtered_df[filtered_df['model_name'] == model].reset_index(drop=True)
                fig_time.add_trace(go.Scatter(
                    x=list(range(len(model_data))),
                    y=model_data['latency_ms'].values,
                    mode='lines',
                    name=model,
                    line=dict(width=2)
                ))
            
            fig_time.update_layout(
                title="Latency Over Time",
                xaxis_title="Request",
                yaxis_title="Latency (ms)",
                hovermode='x unified',
                height=400,
                template='plotly_dark'
            )
            st.plotly_chart(fig_time, use_container_width=True)

            filtered_df = filtered_df.reset_index(drop=True)
            filtered_df["time_index"] = range(len(filtered_df))
            st.subheader("🔋 Battery Percentage Over Time")

            fig_battery_time = go.Figure()

            for model in selected_models:
                model_data = filtered_df[filtered_df["model_name"] == model]

                fig_battery_time.add_trace(go.Scatter(
                    x=model_data["time_index"],
                    y=model_data["battery_percentage"],
                    mode="lines+markers",
                    name=model,
                    line=dict(width=3)
                ))

            fig_battery_time.update_layout(
                title="Battery Drain Over Time While Running Models",
                xaxis_title="Time (Request Order)",
                yaxis_title="Battery Level (%)",
                hovermode="x unified",
                height=450,
                template="plotly_dark"
            )

            st.plotly_chart(fig_battery_time, use_container_width=True)

        
        # Additional visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Model Performance Radar Chart")
            TEMP_MAP = {
                "nominal": 1,
                "fair": 2,
                "serious": 3,
                "critical": 4
            }

            radar_df = filtered_df.groupby("model_name").agg({
                "latency_ms": "mean",
                "battery_percentage": "mean",
                "user_feedback": lambda x: (x == "up").mean() * 100,
                "crash_log": lambda x: (x.notna() & (x != "")).mean() * 100,
                "device_temperature": lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else None
            }).reset_index()

            radar_df["temp_score"] = radar_df["device_temperature"].map(TEMP_MAP)

            fig_radar = go.Figure()

            for _, row in radar_df.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[
                        row["latency_ms"],
                        row["temp_score"],
                        row["battery_percentage"],
                        row["user_feedback"],
                        row["crash_log"]
                    ],
                    theta=["Latency", "Temperature", "Battery", "Feedback %", "Crash %"],
                    fill="toself",
                    name=row["model_name"]
                ))

            fig_radar.update_layout(
                polar=dict(radialaxis=dict(visible=True)),
                template="plotly_dark",
                title="Model Comparison Radar Chart"
            )

            st.plotly_chart(fig_radar, use_container_width=True)
        
        with col2:
            st.subheader("📊 Latency Distribution by Model")
            if 'model_name' in filtered_df.columns and 'latency_ms' in filtered_df.columns:
                fig_model = px.box(
                    filtered_df,
                    x='model_name',
                    y='latency_ms',
                    title='Latency Distribution by Model',
                    template='plotly_dark'
                )
                st.plotly_chart(fig_model, use_container_width=True)




        # Extra overview visualizations
        col3, col4 = st.columns(2)
        with col3:
            if 'user_feedback' in filtered_df.columns and 'model_name' in filtered_df.columns:
                st.subheader("👍👎 Feedback by Model")
                feedback_df = filtered_df.copy()
                feedback_df['user_feedback'] = feedback_df['user_feedback'].fillna("none")
                fig_fb = px.histogram(
                    feedback_df,
                    x="model_name",
                    color="user_feedback",
                    barmode="group",
                    title="User feedback distribution by model",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_fb, use_container_width=True)
        with col4:
            if 'device_temperature' in filtered_df.columns and 'latency_ms' in filtered_df.columns:
                st.subheader("🔥 Temp vs Latency")
                fig_temp = px.scatter(
                    filtered_df,
                    x="device_temperature",
                    y="latency_ms",
                    color="device_model" if "device_model" in filtered_df.columns else None,
                    title="Latency vs Device temperature",
                    template="plotly_dark",
                    
                )
                fig_temp.update_layout(xaxis_title="Temperature Level")
                st.plotly_chart(fig_temp, use_container_width=True)
        
        # Data table
        st.subheader("📋 Raw Data")
        st.dataframe(filtered_df, use_container_width=True)
    with tab2:

        st.header("📌 Per-Run Analysis")

        # Lấy danh sách run_id
        run_ids = df["run_id"].dropna().unique()
        selected_run = st.selectbox("Select a Run ID:", run_ids)

        if selected_run is None:
            st.info("Please select a run_id to view details.")
            st.stop()

        # Filter theo run
        run_df = df[df["run_id"] == selected_run]

        st.subheader(f"📄 Run Information : {selected_run}")

        # === Metrics ===
        colA, colB, colC = st.columns(3)
        colD, colE, colF = st.columns(3)

        # Latency metrics
        colA.metric("Avg Latency (ms)", f"{run_df['latency_ms'].mean():.2f}")
        colB.metric("Min Latency (ms)", f"{run_df['latency_ms'].min():.2f}")
        colC.metric("Max Latency (ms)", f"{run_df['latency_ms'].max():.2f}")
        colD.metric("P95 Latency (ms)", f"{run_df['latency_ms'].quantile(0.95):.2f}")

        # Battery
        colE.metric("Avg Battery (%)", f"{run_df['battery_percentage'].mean():.1f}")

        # Temperature 
        most_common_temp = (
            run_df["device_temperature"].mode().iloc[0]
            if len(run_df["device_temperature"].dropna().mode()) > 0 else "N/A"
        )
        colF.metric("Common Temperature Level", most_common_temp)

        # Crash & Feedback
        crash_rate = (run_df["crash_log"].notna() & (run_df["crash_log"] != "")).mean() * 100
        feedback_up = (run_df["user_feedback"] == "up").mean() * 100

        colA2, colB2 = st.columns(2)
        colA2.metric("Crash Rate (%)", f"{crash_rate:.1f}%")
        colB2.metric("Positive Feedback (%)", f"{feedback_up:.1f}%")

        st.markdown("---")

        # =====================================
        # Charts
        # =====================================
        st.subheader("📈 Run Timeline Visualizations")

        # Latency timeline
        fig_latency = px.line(
            run_df,
            x="request_id",
            y="latency_ms",
            title="Latency Timeline",
            markers=True
        )
        fig_latency.update_layout(template="plotly_dark")
        st.plotly_chart(fig_latency, use_container_width=True)

        # Battery timeline
        fig_battery = px.line(
            run_df,
            x="request_id",
            y="battery_percentage",
            title="Battery Timeline",
            markers=True
        )
        fig_battery.update_layout(template="plotly_dark")
        st.plotly_chart(fig_battery, use_container_width=True)

        # Temperature timeline – numeric hóa 4 mức
        TEMP_MAP = {"nominal": 1, "fair": 2, "serious": 3, "critical": 4}
        run_df["temp_score"] = run_df["device_temperature"].map(TEMP_MAP)

        fig_temp = px.line(
            run_df,
            x="request_id",
            y="temp_score",
            title="Temperature Timeline (iOS Levels)",
            markers=True
        )
        fig_temp.update_yaxes(
            tickvals=[1, 2, 3, 4],
            ticktext=["nominal", "fair", "serious", "critical"]
        )
        fig_temp.update_layout(template="plotly_dark")
        st.plotly_chart(fig_temp, use_container_width=True)

        # Feedback distribution
        fig_fb = px.histogram(
            run_df,
            x="user_feedback",
            title="User Feedback Distribution",
            color="user_feedback"
        )
        fig_fb.update_layout(template="plotly_dark")
        st.plotly_chart(fig_fb, use_container_width=True)

        # Crash logs list
        st.subheader("💥 Crash Logs")
        crash_entries = run_df[run_df["crash_log"].notna() & (run_df["crash_log"] != "")]
        
        if len(crash_entries) == 0:
            st.success("No crash logs for this run 🎉")
        else:
            for idx, row in crash_entries.iterrows():
                st.error(f"Request {row['request_id']}:\n\n{row['crash_log']}")
    with tab3:

        st.header("🆚 Compare Runs")

        run_ids = df["run_id"].dropna().unique()

        selected_runs = st.multiselect(
            "Chọn các Run ID để so sánh",
            options=run_ids,
            default=run_ids[:2] if len(run_ids) >= 2 else run_ids
        )

        if len(selected_runs) == 0:
            st.info("Hãy chọn ít nhất 1 run để so sánh.")
            st.stop()

        compare_df = df[df["run_id"].isin(selected_runs)].copy()

        # ============================
        # SUMMARY TABLE
        # ============================
        st.subheader("📊 Summary Table")

        def summarize(run_id):
            sub = compare_df[compare_df["run_id"] == run_id]

            crash_rate = (sub["crash_log"].notna() & (sub["crash_log"] != "")).mean() * 100
            feedback_up = (sub["user_feedback"] == "up").mean() * 100

            avg_temp = (
                sub["device_temperature"].mode().iloc[0]
                if len(sub["device_temperature"].dropna().mode()) > 0
                else "N/A"
            )

            return {
                "run_id": run_id,
                "model": sub["model_name"].mode().iloc[0],
                "avg_latency": sub["latency_ms"].mean(),
                "avg_temp": avg_temp,
                "avg_battery": sub["battery_percentage"].mean(),
                "crash_rate_%": crash_rate,
                "feedback_positive_%": feedback_up,
            }

        summary_rows = [summarize(r) for r in selected_runs]
        summary_table = pd.DataFrame(summary_rows)

        st.dataframe(summary_table, use_container_width=True)

        st.markdown("---")

        # ============================
        # VISUALIZATIONS
        # ============================

        # ---- Boxplot latency per run ----
        st.subheader("📦 Latency Distribution per Run (Boxplot)")
        fig_box = px.box(
            compare_df,
            x="run_id",
            y="latency_ms",
            color="run_id",
            title="Latency Distribution by Run"
        )
        fig_box.update_layout(template="plotly_dark")
        st.plotly_chart(fig_box, use_container_width=True)

        # ---- Average Latency per run ----
        st.subheader("🚀 Average Latency per Run")
        fig_avg_latency = px.bar(
            summary_table,
            x="run_id",
            y="avg_latency",
            title="Average Latency per Run",
            text_auto=".2f"
        )
        fig_avg_latency.update_layout(template="plotly_dark")
        st.plotly_chart(fig_avg_latency, use_container_width=True)

        # ---- Avg Battery per run ----
        st.subheader("🔋 Average Battery per Run")
        fig_bat = px.bar(
            summary_table,
            x="run_id",
            y="avg_battery",
            title="Average Battery (%) per Run",
            text_auto=".1f"
        )
        fig_bat.update_layout(template="plotly_dark")
        st.plotly_chart(fig_bat, use_container_width=True)

        # ---- Avg Temperature per run ----
        st.subheader("🌡 Temperature Level per Run (Most Common)")
        fig_temp = px.bar(
            summary_table,
            x="run_id",
            y="avg_temp",
            title="Dominant Temperature Level per Run"
        )
        fig_temp.update_layout(template="plotly_dark")
        st.plotly_chart(fig_temp, use_container_width=True)

        # ---- Radar chart per run ----
        st.subheader("🕸 Radar Chart Comparison")

        # Convert temperature to numeric
        TEMP_MAP = {"nominal": 1, "fair": 2, "serious": 3, "critical": 4}
        summary_table["temp_score"] = summary_table["avg_temp"].map(TEMP_MAP)

        radar_df = summary_table.copy()
        radar_df = radar_df.set_index("run_id")

        # Radar requires category columns only
        radar_cols = ["avg_latency", "avg_battery", "temp_score", "crash_rate_%", "feedback_positive_%"]

        fig_radar = go.Figure()

        for rid in radar_df.index:
            fig_radar.add_trace(go.Scatterpolar(
                r=radar_df.loc[rid, radar_cols].values,
                theta=radar_cols,
                fill='toself',
                name=str(rid)
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True),
            ),
            template="plotly_dark",
            title="Radar Chart: Run Comparison",
            showlegend=True
        )

        st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # ============================
        # ADVANCED VISUALIZATIONS
        # ============================

        st.subheader("🔥 Advanced Analytics")

        # ---- Correlation heatmap ----
        st.markdown("### ① Correlation Heatmap")

        corr_df = compare_df.copy()
        corr_df["temp_score"] = corr_df["device_temperature"].map(TEMP_MAP)

        numeric_cols = ["latency_ms", "battery_percentage", "temp_score"]
        corr = corr_df[numeric_cols].corr()

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap: Latency / Battery / Temperature"
        )
        fig_corr.update_layout(template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

        # ---- Battery Drain Rate ----
        st.markdown("### ② Battery Drain Rate per Run")

        def battery_drain(run):
            sub = compare_df[compare_df["run_id"] == run]
            return sub["battery_percentage"].iloc[-1] - sub["battery_percentage"].iloc[0]

        summary_table["battery_drain"] = summary_table["run_id"].apply(battery_drain)

        fig_drain = px.bar(
            summary_table,
            x="run_id",
            y="battery_drain",
            title="Battery Drain per Run",
            text_auto=".1f"
        )
        fig_drain.update_layout(template="plotly_dark")
        st.plotly_chart(fig_drain, use_container_width=True)

        # ---- Temperature Rise Rate ----
        st.markdown("### ③ Temperature Rise Trend per Run")

        def temp_rise(run):
            sub = compare_df[compare_df["run_id"] == run]
            ts = sub["device_temperature"].map(TEMP_MAP)
            return ts.iloc[-1] - ts.iloc[0]

        summary_table["temp_rise"] = summary_table["run_id"].apply(temp_rise)

        fig_rise = px.bar(
            summary_table,
            x="run_id",
            y="temp_rise",
            title="Temperature Rise per Run",
            text_auto=".1f"
        )
        fig_rise.update_layout(template="plotly_dark")
        st.plotly_chart(fig_rise, use_container_width=True)

        # ---- Crash timeline ----
        st.markdown("### ④ Crash Timeline per Run")

        crash_df = compare_df[compare_df["crash_log"].notna() & (compare_df["crash_log"] != "")]

        if len(crash_df) == 0:
            st.success("No crashes detected across selected runs.")
        else:
            fig_crash = px.scatter(
                crash_df,
                x="request_id",
                y="run_id",
                color="run_id",
                size=[10] * len(crash_df),
                title="Crash Timeline",
                labels={"request_id": "Request", "run_id": "Run ID"}
            )
            fig_crash.update_layout(template="plotly_dark")
            st.plotly_chart(fig_crash, use_container_width=True)

else:
    # When shared file is missing or failed to load
    st.title("📊 On-device Latency Dashboard")
    st.error(f"Shared latency file not found or unreadable: {SHARED_LOG}")
    st.subheader("📝 Expected CSV Format")
    sample_data = {
        'request_id': ['req_001', 'req_002', 'req_003'],
        'model_name': ['LFM2-V1-6B', 'LFM2-V1-6B', 'LFM2-VL-450M'],
        'latency_ms': [224.1, 180.5, 195.3],
        'device_model': ['iPhone 13', 'iPhone 14', 'iPhone 15 Pro'],
        'app_version': ['1.0.0', '1.1.0', '2.0.0']
    }
    st.dataframe(pd.DataFrame(sample_data))