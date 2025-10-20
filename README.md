# Live app
# https://crypto-tacker-428.streamlit.app/

# Crypto-Tacker
A real-time cryptocurrency tracker built with Streamlit that displays live data from Binance with price charts, dark/light mode, and search &amp; filter options.

# 💰 Crypto Tracker

A real-time cryptocurrency tracking web app built using **Streamlit**, powered by **Binance** and **CoinGecko APIs**.  
It allows users to view live prices, market caps, 24h changes, and 7-day price charts — all with an elegant dark/light theme toggle.

---

## 🚀 Features

- 🔥 **Real-time data** from Binance (for VANRY/USDT) and CoinGecko (for all major coins)
- 💹 **Interactive charts** showing 7-day price movement
- 🔍 **Search & filter** cryptocurrencies (All / Gainers / Losers)
- 🌗 **Dark & Light mode** toggle with dynamic UI styling
- 🧩 **Auto-refresh** & caching for faster performance

---

## 🛠️ Tech Stack

| Component | Technology |
|------------|-------------|
| Frontend | Streamlit |
| Data Sources | Binance API, CoinGecko API |
| Charts | Plotly |
| Language | Python |
| Data Handling | Pandas |

---

## 📦 Installation

### 1️⃣ Clone this repository
```bash
git clone https://github.com/<your-username>/crypto-tracker-streamlit.git
cd crypto-tracker-streamlit
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Requirements
streamlit
requests
pandas
plotly

