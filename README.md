# 📈 Intelligent Trading Dashboard and Risk Calculator 

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B.svg?logo=streamlit&logoColor=white)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Scikit--Learn-orange.svg)

A professional-grade, AI-powered stock market terminal built with Python. This application combines advanced technical charting, Machine Learning price predictions, Natural Language Processing (NLP) news sentiment, and strict risk management execution into a single, cohesive Streamlit dashboard.

---

## 📸 Screenshots
Main Charts:

<img width="2452" height="1233" alt="image" src="https://github.com/user-attachments/assets/49add17c-f585-4678-8251-797cf4ac5489" />

ML Price Prediction and AI Briefing Section:

<img width="2479" height="1204" alt="image" src="https://github.com/user-attachments/assets/92cf3164-323c-426a-a8c0-28f9c91acc58" />

"Smarter" Trade Planner Sidebar:

<img width="434" height="875" alt="image" src="https://github.com/user-attachments/assets/52a34447-b460-4b82-846f-45fb611ba204" />


Trade Planner lines/levels shown on chart:

<img width="2493" height="1229" alt="image" src="https://github.com/user-attachments/assets/c16bbc88-b394-46ef-8d30-fb679227fbc4" />


---

## ✨ Key Features

* **Advanced Technical Charting:** Interactive Plotly candlestick charts featuring dynamic SMA crossovers, Bollinger Bands, MACD, and RSI momentum oscillators.
* **Predictive AI Engine:** A Random Forest Machine Learning model that trains on the fly using engineered historical features (Volatility, Momentum, Volume) to forecast the next period's price action.
* **Automated Analyst Briefing:** A heuristic logic engine that reads technical chart conditions and formulates human-readable "Bull" and "Bear" cases.
* **Live News & Sentiment Analysis:** Scrapes the latest Yahoo Finance RSS feeds and runs them through TextBlob NLP to gauge the current media mood (Bullish, Bearish, or Neutral).
* **Smart Trade Execution Planner:** An interactive sidebar calculator that auto-fills AI targets and technical stop-losses to calculate exact position sizing based on your personal account risk percentage. Visualizes the Risk/Reward ratio directly on the main chart.

---

## 🛠️ Technology Stack

* **Frontend:** Streamlit, Plotly Express, Plotly Graph Objects
* **Data Fetching:** `yfinance`, Yahoo Finance RSS, `urllib`
* **Data Processing:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (`RandomForestRegressor`)
* **Natural Language Processing:** TextBlob

---

## 🚀 How to Run Locally

**1. Clone the repository:**
```bash
git clone [https://github.com/r-kainth/intelligent-trading-dashboard-risk-calculator.git](https://github.com/r-kainth/intelligent-trading-dashboard-risk-calculator.git)
cd intelligent-trading-dashboard-risk-calculator
```

**2. Create a virtual environment (recommended):** 
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the application:**
```bash
streamlit run main.py
```

## ⚠️ Disclaimer
**Educational Purposes Only.** This software is for educational and research purposes only. Do not use this application to make real-world financial decisions. 
The Machine Learning predictions and sentiment analysis are highly experimental and are not indicative of future market performance. 
Always consult with a registered financial advisor before trading.
