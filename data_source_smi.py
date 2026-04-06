import yfinance as yf
import pandas as pd
from datetime import datetime

class DataSource:
    def __init__(self):
        # The 20 current SMI (Swiss Market Index) stock tickers
        self.smi_tickers = [
            "ABBN.SW", "ALC.SW", "CFR.SW", "GEBN.SW", "GIVN.SW", 
            "HOLN.SW", "KNIN.SW", "LOGN.SW", "LONN.SW", "NESN.SW", 
            "NOVN.SW", "PGHN.SW", "ROG.SW", "SCMN.SW", "SIKA.SW", 
            "SLHN.SW", "SOON.SW", "SREN.SW", "UBSG.SW", "ZURN.SW"
        ]

    def get_smi_data(self):
        """Fetch real-time data for all SMI stocks"""
        try:
            # Download data for all tickers at once
            # We use '1d' period to get the most recent closing/current price
            data = yf.download(self.smi_tickers, period="1d", interval="1m", group_by='ticker', progress=False)
            
            smi_list = []
            
            for ticker in self.smi_tickers:
                # Get the last available price row for this ticker
                ticker_data = data[ticker]
                if not ticker_data.empty:
                    last_price = ticker_data['Close'].iloc[-1]
                    # Note: yfinance 'Close' for '1d' period is the live price during market hours
                    
                    smi_list.append({
                        'Ticker': ticker.replace(".SW", ""), # Clean up name (e.g., NESN)
                        'Price (CHF)': round(last_price, 2),
                        'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

            # Convert to a clean table
            df = pd.DataFrame(smi_list)
            return df

        except Exception as error:
            print(f"Error fetching SMI data: {error}")
            return pd.DataFrame()

# --- Example Usage ---
source = DataSource()
smi_table = source.get_smi_data()

if not smi_table.empty:
    print("--- Current SMI Stock Prices ---")
    print(smi_table.to_string(index=False))
else:
    print("Could not retrieve data. Check your internet connection.")