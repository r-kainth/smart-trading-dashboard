import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_fetcher import get_stock_data, get_company_info
from utils.charts import create_candlestick_chart
from utils.indicators import add_technical_indicators, get_rsi_metrics
from utils.ml_features import generate_ml_features 
from utils.ai_models import train_and_predict, generate_analyst_briefing
from utils.sentiment_analyzer import get_news_sentiment
from utils.risk_calculator import calculate_trade_risk

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
    time_period = st.selectbox("Time Period", list(VALID_INTERVALS.keys()), index=7) # Default to "1y"

with col3:
    # Dynamically update the intervals based on the selected period!
    valid_intervals_for_period = VALID_INTERVALS[time_period]
    
    # Try to default to "1d" if it's available in the list, otherwise default to the first item
    default_index = valid_intervals_for_period.index("1d") if "1d" in valid_intervals_for_period else 0
    time_interval = st.selectbox("Candle Interval", valid_intervals_for_period, index=default_index)

if ticker:
    # 1. Fetch data
    raw_data = get_stock_data(ticker, time_period=time_period, time_interval=time_interval)
    company_info = get_company_info(ticker) # Fetch the new company info!
    
    if raw_data.empty:
        st.error(f"No data found for {ticker}. The ticker might be invalid, or Yahoo Finance may be temporarily blocking the request.")
    else:
        # 2. Add the math
        analyzed_data = add_technical_indicators(raw_data)
        
        # --- NEW: TOP METRICS ROW ---
        st.markdown("---") # Adds a subtle divider line
        
        # Extract the latest numbers for our metrics
        # Extract the latest numbers for our metrics
        latest_close = analyzed_data['Close'].iloc[-1]
        prev_close = analyzed_data['Close'].iloc[-2] if len(analyzed_data) > 1 else latest_close
        amt_change = latest_close - prev_close
        pct_change = ((latest_close - prev_close) / prev_close) * 100
        price_state = f"{amt_change:+.2f} ({pct_change:+.2f}%)"
        
        # --- NEW: Day Range ---
        latest_high = analyzed_data['High'].iloc[-1]
        latest_low = analyzed_data['Low'].iloc[-1]
        day_range = f"\${latest_low:.2f} - \${latest_high:.2f}" # ignore syntax warning, this is correct for f-string formatting
        
        # --- NEW: Relative Volume ---
        latest_volume = analyzed_data['Volume'].iloc[-1]
        avg_vol_20 = analyzed_data['Volume'].rolling(20).mean().iloc[-1]
        if not pd.isna(avg_vol_20) and avg_vol_20 > 0:
            vol_delta_pct = ((latest_volume - avg_vol_20) / avg_vol_20) * 100
            vol_state = f"{vol_delta_pct:+.1f}% vs 20d Avg"
        else:
            vol_state = "N/A"
        
        # --- SMART RSI LOGIC ---
        latest_rsi, rsi_state, delta_color, delta_arrow = get_rsi_metrics(analyzed_data['RSI'].iloc[-1])

        # --- SMART SMA LOGIC ---
        latest_sma20 = analyzed_data['SMA_20'].iloc[-1] if not pd.isna(analyzed_data['SMA_20'].iloc[-1]) else 0
        if latest_sma20 > 0:
            sma_distance_pct = ((latest_close - latest_sma20) / latest_sma20) * 100
            sma_state = f"{sma_distance_pct:+.2f}% (Price vs SMA)"
        else:
            sma_state = "N/A"

        # Create 5 columns for the metrics!
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Current Price", f"${latest_close:.2f}", price_state)
        m2.metric("Day Range", day_range) 
        m3.metric("Volume", f"{latest_volume:,.0f}", vol_state) 
        m4.metric("RSI (14)", f"{latest_rsi:.1f}", rsi_state, delta_color=delta_color, delta_arrow=delta_arrow) 
        m5.metric("SMA 20", f"${latest_sma20:.2f}", sma_state)
        
        
        # ==========================================
        # 🧮 SMART TRADE PLANNER (SIDEBAR)
        # ==========================================
        # 1. We initialize a session state variable to "remember" our trade levels
        if 'trade_levels' not in st.session_state:
            st.session_state.trade_levels = None

        st.sidebar.header("🧮 Smart Trade Planner")
        st.sidebar.write("Plan your position sizing using AI defaults or custom levels.")

        account_size = st.sidebar.number_input("Account Size ($)", min_value=100.0, value=10000.0, step=100.0)
        risk_pct = st.sidebar.slider("Account Risk (%)", min_value=0.5, max_value=25.0, value=2.0, step=0.1)

        st.sidebar.markdown("---")

        custom_entry = st.sidebar.number_input("Entry Price ($)", min_value=0.01, value=float(latest_close), step=0.50)
        
        default_stop = float(analyzed_data['BB_lower'].iloc[-1]) if not pd.isna(analyzed_data['BB_lower'].iloc[-1]) else float(latest_close * 0.95)
        if default_stop >= custom_entry: default_stop = custom_entry * 0.98 
        custom_stop = st.sidebar.number_input("Stop Loss ($)", min_value=0.01, value=default_stop, step=0.50)
        
        # NOTE: We temporarily default the target to a 2:1 RR since the ML model hasn't run yet in the code sequence
        default_target = float(custom_entry + ((custom_entry - custom_stop) * 2))
        custom_target = st.sidebar.number_input("Target Price ($)", min_value=0.01, value=default_target, step=0.50)

        if st.sidebar.button("Calculate Position", use_container_width=True, type="primary"):
            results, error = calculate_trade_risk(account_size, risk_pct, custom_entry, custom_stop, custom_target)
            
            if error:
                st.sidebar.error(error)
                st.session_state.trade_levels = None # Clear chart lines on error
            else:
                st.sidebar.success(f"**Buy {results['shares']:,} Shares**")
                
                c1, c2 = st.sidebar.columns(2)
                c1.metric("Total Capital", f"${results['position_size']:,.2f}")
                c2.metric("Max Risk", f"${results['dollar_risk']:,.2f}")
                
                c3, c4 = st.sidebar.columns(2)
                c3.metric("Est. Profit", f"${results['expected_profit']:,.2f}")
                c4.metric("R/R Ratio", f"{results['rr_ratio']:.2f}x")
                
                if results['position_size'] > account_size:
                    st.sidebar.warning("⚠️ Warning: Position size exceeds account balance (Requires Margin).")
                
                # SAVE THE LEVELS TO MEMORY SO THE CHART CAN DRAW THEM!
                st.session_state.trade_levels = {
                    'entry': custom_entry,
                    'stop': custom_stop,
                    'target': custom_target
                }
                
        if st.sidebar.button("Clear Chart Lines", use_container_width=True):
            st.session_state.trade_levels = None

        # --- THE MAIN CHART ---
        # Notice we now pass our saved trade_levels into the chart function!
        fig = create_candlestick_chart(analyzed_data, ticker, trade_levels=st.session_state.trade_levels)
        st.plotly_chart(fig, width='stretch')

        # ==========================================
        # 🤖 MACHINE LEARNING SECTION
        # ==========================================
        st.markdown("---")
        st.subheader("🤖 AI Price Prediction Model")
        
        # 1. Generate the heavy ML features
        ml_data = generate_ml_features(raw_data)
        
        # Initialize prediction as None. It only gets updated if the ML model runs successfully!
        prediction = None 
        
        # 2. The Safeguard! Check if we have enough data to train a model
        if len(ml_data) < 100:
            st.warning("⚠️ Insufficient data for reliable ML prediction. Please select a longer 'Time Period' (e.g., 1y, 2y, 5y).")
        else:
            with st.spinner("Training Random Forest Model on historical data..."):
                # 3. Run the model
                prediction, accuracy, feature_importances = train_and_predict(ml_data)
                
                # 4. Calculate if the prediction is higher or lower than the current price
                predicted_change = prediction - latest_close
                predicted_pct = (predicted_change / latest_close) * 100
                
                # 5. Build the UI
                ai_col1, ai_col2 = st.columns([1, 1.5]) # Left column is smaller, right is wider
                
                with ai_col1:
                    st.success("✅ Model trained successfully!")
                    st.metric(
                        label="Next Period Prediction", 
                        value=f"${prediction:.2f}", 
                        delta=f"{predicted_change:+.2f} ({predicted_pct:+.2f}%) expected"
                    )
                    st.info(f"**Test Accuracy:** {accuracy:.1f}%")
                    st.caption("Note: Accuracy is based on testing against historical data unseen by the model during training. Not financial advice.")
                
                with ai_col2:
                    # Draw a horizontal bar chart of the most important features
                    st.write("**Top Drivers of this Prediction:**")
                    fig_features = px.bar(
                        feature_importances, 
                        x='Importance', 
                        y='Feature', 
                        orientation='h',
                        color_discrete_sequence=['#636EFA'] # A nice blue color
                    )
                    fig_features.update_layout(
                        template="plotly_dark",
                        height=250, 
                        margin=dict(l=0, r=0, t=0, b=0),
                        yaxis={'categoryorder':'total ascending'} # Puts the biggest bar at the top
                    )
                    st.plotly_chart(fig_features, width='stretch')
                
        # ==========================================
        # 📝 AI ANALYST BRIEFING SECTION
        # ==========================================
        # Notice this is now OUTSIDE the ML 'else' block! It will run every time.
        st.markdown("---")
        st.subheader("📝 Automated Analyst Briefing")
        
        # We pass prediction, which will be either a dollar amount or 'None'
        bull_case, bear_case, verdict = generate_analyst_briefing(analyzed_data, prediction)
        
        # Display the Verdict at the top
        st.markdown(f"**{verdict}**")
        
        # Display Bull vs Bear in columns
        brief_col1, brief_col2 = st.columns(2)
        with brief_col1:
            st.success("**The Bull Case (Why it could go up):**")
            for point in bull_case:
                st.write(f"📈 {point}")
                
        with brief_col2:
            st.error("**The Bear Case (Why it could go down):**")
            for point in bear_case:
                st.write(f"📉 {point}")
        
        # ==========================================
        # 📰 LIVE NEWS & SENTIMENT SECTION
        # ==========================================
        st.markdown("---")
        st.subheader("📰 Live News & Sentiment Analysis")
        
        # Fetch and analyze the news
        news_articles, avg_polarity, overall_mood = get_news_sentiment(ticker)
        
        if news_articles:
            # Create two columns: one for the articles, one for the sentiment meter
            news_col, meter_col = st.columns([2, 1])
            
            with meter_col:
                st.write("**Overall News Sentiment**")
                # Display a visual metric for the mood
                if "Bullish" in overall_mood:
                    st.success(f"**{overall_mood}**")
                elif "Bearish" in overall_mood:
                    st.error(f"**{overall_mood}**")
                else:
                    st.warning(f"**{overall_mood}**")
                    
                # Show the raw NLP score
                st.metric("Raw Polarity Score", f"{avg_polarity:+.2f}", help="Scores range from -1.0 (Very Negative) to +1.0 (Very Positive)")
                st.caption("Powered by Natural Language Processing (TextBlob)")

            with news_col:
                st.write("**Latest Headlines (from Yahoo Finance):**")
                for article in news_articles:
                    # Use Markdown to create clickable links
                    st.markdown(f"[{article['title']}]({article['link']})")
                    st.caption(f"{article['publisher']} | {article['date']} | NLP Score: {article['sentiment']:+.2f}")
        else:
            st.write("No recent news articles found for this ticker.")

        # --- BOTTOM TABS ---
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["Company Profile", "Financial Summary", "Raw Data Table"])
        
        with tab1:
            if company_info:
                st.subheader(company_info.get('longName', ticker.upper()))
                st.write(f"**Sector:** {company_info.get('sector', 'N/A')} | **Industry:** {company_info.get('industry', 'N/A')} | **Location:** {company_info.get('city', 'N/A')}, {company_info.get('country', 'N/A')}")
                st.write(company_info.get('longBusinessSummary', 'No summary available.'))
            else:
                st.write("Company profile data not available.")
                
        with tab2:
            if company_info:
                f1, f2 = st.columns(2)
                with f1:
                    st.write(f"**Market Cap:** ${company_info.get('marketCap', 0):,}")
                    
                    # Safely check if these metrics are numbers before applying the .2f formatting
                    t_pe = company_info.get('trailingPE')
                    st.write(f"**Trailing P/E:** {f'{t_pe:.2f}' if isinstance(t_pe, (int, float)) else 'N/A'}")
                    
                    f_pe = company_info.get('forwardPE')
                    st.write(f"**Forward P/E:** {f'{f_pe:.2f}' if isinstance(f_pe, (int, float)) else 'N/A'}")
                    
                    eps = company_info.get('forwardEps')
                    st.write(f"**EPS (Forward):** {f'{eps:.2f}' if isinstance(eps, (int, float)) else 'N/A'}")
                with f2:
                    st.write(f"**52 Week High:** ${company_info.get('fiftyTwoWeekHigh', 'N/A')}")
                    st.write(f"**52 Week Low:** ${company_info.get('fiftyTwoWeekLow', 'N/A')}")
                    st.write(f"**Average Volume:** {company_info.get('averageVolume', 0):,}")
            else:
                st.write("Financial summary data not available.")
                
        with tab3:
            st.write("Raw historical data, respective of the time period and candle interval shown in the chart, with technical indicators:")
            st.dataframe(analyzed_data)
