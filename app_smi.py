import streamlit as st  # Web app framework
import time  # For creating delays
from datetime import datetime  # For working with time
from data_source_smi import DataSource  # Our data getting class
from charts_smi import ChartCreator  # Our chart creating class

# Configure our web page
st.set_page_config(
    page_title="SMI Real-time Dashboard", 
    page_icon="🇨🇭", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

def main():
    """Main function that runs our SMI dashboard"""

    # 1. Page Setup
    st.title("📊 Swiss Market Index (SMI) Live")
    st.markdown("Real-time tracking of the top 20 Swiss Blue Chip stocks.")
    st.markdown("---")

    # 2. Sidebar Controls
    st.sidebar.header("Dashboard Settings")
    auto_refresh = st.sidebar.checkbox(
        "Enable Auto Refresh",
        value=True,
        help="Automatically update stock data every few seconds"
    )

    refresh_interval = st.sidebar.slider(
        "Update Every (seconds)",
        min_value=5,
        max_value=60,
        value=10
    )

    # 3. Initialize Classes
    data_source = DataSource()
    chart_creator = ChartCreator()

    # 4. Content Containers
    status_container = st.empty()
    metrics_container = st.container() # Container for the 3 top metrics
    smi_container = st.empty()

    update_count = 0

    # 5. The Live Update Loop
    # If auto_refresh is off, it runs once. If on, it loops.
    while True:
        update_count += 1
        
        # Fetch SMI Data
        smi_data = data_source.get_smi_data()

        # Update Status
        current_time = datetime.now().strftime("%H:%M:%S")
        status_container.info(f"Last updated: {current_time} (Update #{update_count})")

        # --- SMI SECTION ---
        if not smi_data.empty:
            # Update Metrics (at the top)
            with metrics_container:
                chart_creator.create_summary_metrics(smi_data)
            
            # Update Chart
            with smi_container.container():
                st.subheader("SMI Price Comparison (CHF)")
                fig = chart_creator.create_smi_chart(smi_data)
                st.plotly_chart(fig, use_container_width=True, key=f"smi_chart_{update_count}")
                
                # Optional: Show the raw data table below the chart
                with st.expander("View Raw Data Table"):
                    st.dataframe(smi_data, use_container_width=True)
        else:
            smi_container.warning("Waiting for data from Yahoo Finance...")

        # 6. Loop Logic
        if not auto_refresh:
            break
            
        time.sleep(refresh_interval)
        # Streamlit-specific trick: this ensures the app re-runs properly
        if auto_refresh:
            st.rerun()

# The Ignition Switch
if __name__ == "__main__":
    main()