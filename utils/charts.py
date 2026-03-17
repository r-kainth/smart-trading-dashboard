import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_candlestick_chart(df, ticker):
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, 
        vertical_spacing=0.04, # Increased slightly for cleaner separation
        row_heights=[0.5, 0.15, 0.15, 0.2],
        subplot_titles=(f"{ticker.upper()} Price & Moving Averages", "Volume", "MACD", "RSI & Stochastic")
    )

    # ROW 1: Price, SMA, and Bollinger Bands (Uses default "legend")
    fig.add_trace(go.Candlestick(
        x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"
    ), row=1, col=1)
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='blue', width=1), name='SMA 20'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], line=dict(color='gray', width=1, dash='dot'), name='Upper BB'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], line=dict(color='gray', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='Lower BB'), row=1, col=1)

    # ROW 2: Volume (Hidden from all legends)
    colors = ['green' if row['Close'] >= row['Open'] else 'red' for index, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name="Volume", showlegend=False), row=2, col=1)

    # ROW 3: MACD (Assigned to "legend2")
    if 'MACD' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue', width=1), name='MACD Line', legend="legend2"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='orange', width=1), name='Signal Line', legend="legend2"), row=3, col=1)
        macd_colors = ['green' if val >= 0 else 'red' for val in df['MACD_Hist']]
        fig.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], marker_color=macd_colors, name='Histogram', legend="legend2"), row=3, col=1)

    # ROW 4: RSI and Stochastic (Assigned to "legend3")
    if 'RSI' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1), name='RSI', legend="legend3"), row=4, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['Stoch_K'], line=dict(color='cyan', width=1), name='Stoch %K', legend="legend3"), row=4, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="gray", row=4, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="gray", row=4, col=1)

    # Configure the positions of our multiple legends!
    fig.update_layout(
        template="plotly_dark",
        height=900,
        margin=dict(l=20, r=20, t=60, b=20),
        
        # Legend 1: Top chart
        legend=dict(
            title="Price & Trend",
            y=1.0,           # 1.0 is the very top of the figure
            yanchor="top",
            x=1.01,          # Just slightly outside the right edge of the chart
            xanchor="left"
        ),
        # Legend 2: MACD chart
        legend2=dict(
            title="MACD",
            y=0.34,          # Placed roughly 34% up from the bottom (next to row 3)
            yanchor="top",
            x=1.01,
            xanchor="left"
        ),
        # Legend 3: Momentum chart
        legend3=dict(
            title="Momentum",
            y=0.17,          # Placed roughly 17% up from the bottom (next to row 4)
            yanchor="top",
            x=1.01,
            xanchor="left"
        )
    )
    
    fig.update_xaxes(rangeslider_visible=False)

    return fig