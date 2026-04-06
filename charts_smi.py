import plotly.graph_objects as go
import streamlit as st

class ChartCreator:

    def create_smi_chart(self, smi_data):
        """Create a beautiful chart for SMI stock prices"""

        # Check if we have data to display
        if smi_data.empty:
            return go.Figure()

        # Create new figure
        fig = go.Figure()

        # Add bars to our chart
        # We use 'Ticker' for X and 'Price (CHF)' for Y based on our previous logic
        fig.add_trace(go.Bar(
            x=smi_data['Ticker'],  
            y=smi_data['Price (CHF)'],
            text=[f"{price:.2f}" for price in smi_data['Price (CHF)']],
            textposition='outside', # Move text outside for better readability with 20 bars
            marker_color='royalblue', # A professional blue for Swiss Blue Chips
            name='SMI Stock Prices'
        ))

        # Customize chart appearance
        fig.update_layout(
            title="Swiss Market Index (SMI) - Live Prices",
            xaxis_title="Stock Ticker",
            yaxis_title="Price (CHF)",
            height=500, # Increased height to accommodate more data
            template="plotly_dark",
            xaxis={'categoryorder':'total descending'} # Sorts bars from highest to lowest price
        )

        # Rotate x-axis labels so they don't overlap
        fig.update_xaxes(tickangle=45)

        return fig

    def create_summary_metrics(self, smi_data):
        """Create summary information about the SMI portfolio"""

        if not smi_data.empty:
            # Calculate metrics
            avg_price = smi_data['Price (CHF)'].mean()
            max_stock = smi_data.loc[smi_data['Price (CHF)'].idxmax()]
            min_stock = smi_data.loc[smi_data['Price (CHF)'].idxmin()]

            # Display summary metrics in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Avg SMI Price", f"{avg_price:.2f} CHF")
            with col2:
                st.metric("Most Expensive", f"{max_stock['Price (CHF)']:,.2f} CHF", max_stock['Ticker'])
            with col3:
                st.metric("Least Expensive", f"{min_stock['Price (CHF)']:,.2f} CHF", min_stock['Ticker'])