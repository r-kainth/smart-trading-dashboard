import streamlit as st
from utils.data_fetcher import get_stock_data
from utils.charts import create_candlestick_chart
from utils.indicators import add_technical_indicators

st.set_page_config(page_title="Smart Trading Dashboard", layout="wide")
st.title("📈 Smart Trading Dashboard")
st.write("Welcome to your AI-powered stock analysis tool. Enter a ticker below to view advanced technical analysis, momentum indicators, and risk management data to support your next trade!") 

# Create 3 columns for our user inputs so they sit nicely side-by-side
col1, col2, col3 = st.columns(3)

# 1. We create a dictionary mapping rules for Yahoo Finance API
# The key is the Period, the list is the valid Intervals for that period
VALID_INTERVALS = {
    "1d": ["1m", "2m", "5m", "15m", "30m", "1h"],
    "5d": ["1m", "2m", "5m", "15m", "30m", "1h", "1d"],
    "1wk": ["1m", "2m", "5m", "15m", "30m", "1h", "1d"], # same as 5d
    "1mo": ["2m", "5m", "15m", "30m", "1h", "1d", "1wk"],
    "3mo": ["1d", "1wk", "1mo"], # Intraday not allowed past 60 days
    "6mo": ["1d", "1wk", "1mo"],
    "ytd": ["1d", "1wk", "1mo"],
    "1y": ["1d", "1wk", "1mo", "3mo"],
    "2y": ["1d", "1wk", "1mo", "3mo"],
    "5y": ["1d", "1wk", "1mo", "3mo"],
    "max": ["1d", "1wk", "1mo", "3mo"]
}

with col1:
    ticker = st.text_input("Enter a Ticker Symbol:", "AAPL")

with col2:
    # Get the list of all periods (the keys from our dictionary)
    time_period = st.selectbox("Time Period", list(VALID_INTERVALS.keys()), index=6) 

with col3:
    # Dynamically update the intervals based on the selected period!
    valid_intervals_for_period = VALID_INTERVALS[time_period]
    
    # Try to default to "1d" if it's available in the list, otherwise default to the first item
    default_index = valid_intervals_for_period.index("1d") if "1d" in valid_intervals_for_period else 0
    time_interval = st.selectbox("Candle Interval", valid_intervals_for_period, index=default_index)

if ticker:
    # 1. Fetch data
    raw_data = get_stock_data(ticker, time_period=time_period, time_interval=time_interval)
    
    # Error Handling: Check if the API returned an empty dataframe
    if raw_data.empty:
        st.error(f"No data found for {ticker}. The ticker might be invalid, or Yahoo Finance may be temporarily blocking the request.")
    else:
        # 2. Add the math
        analyzed_data = add_technical_indicators(raw_data)
        
        # 3. Create and show the massive chart
        fig = create_candlestick_chart(analyzed_data, ticker)
        st.plotly_chart(fig, width='stretch')
        
        with st.expander("View Analyzed Data Table"):
            st.dataframe(analyzed_data)