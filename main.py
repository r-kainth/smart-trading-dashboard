import streamlit as st
import yfinance as yf

# 1. Title
st.title("Stock Dashboard")

# 2. Input
ticker = st.text_input("Enter Ticker", "AAPL")

# 3. Get Data
if ticker:
    stock = yf.Ticker(ticker)
    # Get just the last row of data to test
    data = stock.history(period="1d")
    
    # 4. Display
    st.write(f"Latest Close Price for {ticker}:")
    st.write(data)