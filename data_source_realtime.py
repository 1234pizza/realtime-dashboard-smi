import yfinance as yf
import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime

class DataSource:
    def __init__(self):
        self.index_config = {
            "SMI": ["NESN.SW", "NOVN.SW", "ROG.SW", "UBSG.SW", "ZURN.SW", "ABBN.SW", "CFR.SW", "ALC.SW", "SREN.SW", "SIKA.SW", "LONN.SW", "GIVN.SW", "HOLN.SW", "GEBN.SW", "SCMN.SW"],
            "DAX": ["SAP.DE", "SIE.DE", "ALV.DE", "DTE.DE", "AIR.DE", "MBG.DE", "BMW.DE", "BAS.DE", "BAYN.DE", "ADS.DE", "IFX.DE", "MUV2.DE", "DHL.DE", "RWE.DE", "DBK.DE"],
            "SP500": ["AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "BRK-B", "TSLA", "V", "JPM", "UNH", "JNJ", "XOM", "WMT", "MA"],
            "NASDAQ": ["AAPL", "MSFT", "AMZN", "NVDA", "AVGO", "META", "ADBE", "COST", "PEP", "NFLX", "AMD", "CMCSA", "TMUS", "TXN", "INTC"]
        }
        self.cols = ['Index', 'Ticker', 'Price', '14d RSI', '2m Velocity %', '1h Change %', 'Today %', 'Last Sync']

    def calculate_rsi(self, series, period=14):
        """
        Calculates RSI using Wilder's Smoothing (RMA).
        Pandas ewm with com=(period - 1) is the exact math for Wilder's.
        """
        delta = series.diff()
        gain = delta.clip(lower=0)
        loss = -1 * delta.clip(upper=0)
        
        # Standard Wilder's Moving Average (RMA)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @st.cache_data(ttl=115)
    def get_velocity_data(_self):
        try:
            all_tickers = []
            ticker_to_index = {}
            for idx_name, tickers in _self.index_config.items():
                for t in tickers:
                    if t not in all_tickers:
                        all_tickers.append(t)
                        ticker_to_index[t] = idx_name

            # 1m data for short-term; 90d for high-stability RSI
            data_1m = yf.download(all_tickers, period="2d", interval="1m", group_by='ticker', progress=False)
            data_1d = yf.download(all_tickers, period="90d", interval="1d", group_by='ticker', progress=False)
            
            if data_1m.empty or data_1d.empty:
                return pd.DataFrame(columns=_self.cols)

            combined_results = []
            for ticker in all_tickers:
                try:
                    if ticker not in data_1m.columns.get_level_values(0):
                        continue
                        
                    df_1m = data_1m[ticker].dropna()
                    df_1d = data_1d[ticker].dropna()
                    
                    if len(df_1m) < 61 or len(df_1d) < 30:
                        continue
                    
                    curr_p = df_1m['Close'].iloc[-1]
                    
                    # Short-term metrics
                    prev_2m_p = df_1m['Close'].iloc[-3]
                    velocity_2m = ((curr_p - prev_2m_p) / prev_2m_p) * 100
                    
                    prev_1h_p = df_1m['Close'].iloc[-61]
                    change_1h = ((curr_p - prev_1h_p) / prev_1h_p) * 100

                    # --- ULTRA-STABLE RSI LOGIC ---
                    # We use ONLY the historical daily closes to keep the RSI anchored.
                    # We add the live price as the 'current' day's close.
                    history = df_1d['Close'].copy()
                    
                    # Strip out today's partial daily candle if yfinance included it
                    today_date = datetime.now().date()
                    history = history[history.index.date < today_date]
                    
                    # Combine history with exactly ONE live data point
                    combined_close = pd.concat([history, pd.Series([curr_p])])
                    
                    rsi_series = _self.calculate_rsi(combined_close, period=14)
                    current_rsi = rsi_series.iloc[-1]

                    # Today % Change
                    today_open = df_1d['Open'].iloc[-1]
                    today_pct = ((curr_p - today_open) / today_open) * 100
                    
                    combined_results.append({
                        'Index': ticker_to_index[ticker],
                        'Ticker': ticker.split('.')[0],
                        'Price': round(curr_p, 2),
                        '14d RSI': round(current_rsi, 2) if not np.isnan(current_rsi) else "N/A",
                        '2m Velocity %': round(velocity_2m, 3),
                        '1h Change %': round(change_1h, 2),
                        'Today %': round(today_pct, 2),
                        'Last Sync': df_1m.index[-1].strftime('%H:%M:%S')
                    })
                except Exception:
                    continue 

            return pd.DataFrame(combined_results) if combined_results else pd.DataFrame(columns=_self.cols)
            
        except Exception as e:
            st.error(f"Data Fetching Error: {str(e