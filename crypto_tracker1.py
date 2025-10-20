import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Crypto Tracker",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


CMC_API_KEY = None  

# Custom CSS for better styling
def load_css(dark_mode):
    if dark_mode:
        st.markdown("""
        <style>
        .stApp {
            background-color: #111827;
            color: #ffffff;
        }
        .crypto-card {
            background: linear-gradient(145deg, #1f2937, #111827);
            border-radius: 16px;
            padding: 24px;
            margin: 12px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #374151;
            transition: all 0.3s ease;
        }
        .crypto-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
        }
        .metric-card {
            background: #374151;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .vanry-badge {
            background: #F3BA2F;
            color: #000;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 8px;
        }
        .positive {
            color: #10b981;
            font-weight: bold;
        }
        .negative {
            color: #ef4444;
            font-weight: bold;
        }
        h1, h2, h3 {
            color: #ffffff;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #f9fafb;
            color: #111827;
        }
        .crypto-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin: 12px 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border: 1px solid #e5e7eb;
            transition: all 0.3s ease;
        }
        .crypto-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-card {
            background: #f3f4f6;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .vanry-badge {
            background: #F3BA2F;
            color: #000;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 8px;
        }
        .positive {
            color: #10b981;
            font-weight: bold;
        }
        .negative {
            color: #ef4444;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True
if 'selected_coin' not in st.session_state:
    st.session_state.selected_coin = None
if 'coins_data' not in st.session_state:
    st.session_state.coins_data = None


load_css(st.session_state.dark_mode)


if st.session_state.dark_mode:
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #0000FF !important;
            color: white !important;
            border: none !important;
        }
        div.stButton > button:hover {
            background-color: #dc2626 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        div.stButton > button {
            background-color: #0000FF !important;
            color: white !important;
            border: none !important;
        }
        div.stButton > button:hover {
            background-color: #b91c1c !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)



@st.cache_data(ttl=60)
def fetch_vanry_from_binance():
    """Fetch VANRY/USDT data from Binance"""
    try:
        
        ticker_url = "https://api.binance.com/api/v3/ticker/24hr"
        params = {'symbol': 'VANRYUSDT'}
        
        response = requests.get(ticker_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
       
        price = float(data['lastPrice'])
        price_change_24h = float(data['priceChangePercent'])
        high_24h = float(data['highPrice'])
        low_24h = float(data['lowPrice'])
        volume = float(data['volume']) * price  # Volume in USDT
        
        vanry_coin = {
            'id': 'vanry-binance',
            'symbol': 'vanry',
            'name': 'Vanry',
            'image': 'https://cryptologos.cc/logos/thumbs/vanry.png?v=029',  
            'current_price': price,
            'market_cap': 0,  
            'market_cap_rank': 1,  
            'price_change_percentage_24h': price_change_24h,
            'high_24h': high_24h,
            'low_24h': low_24h,
            'total_volume': volume,
            'circulating_supply': 0,
            'source': 'binance'
        }
        
        return vanry_coin
    except Exception as e:
        st.warning(f"Could not fetch VANRY from Binance: {str(e)}")
        return None

@st.cache_data(ttl=60)
def fetch_coins_from_coingecko():
    """Fetch cryptocurrency data from CoinGecko API as fallback"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 50,
        'page': 1,
        'sparkline': False,
        'price_change_percentage': '24h'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
       
        for coin in data:
            coin['source'] = 'coingecko'
        
        return data
    except Exception as e:
        st.error(f"Error fetching data from CoinGecko: {str(e)}")
        return []

@st.cache_data(ttl=60)
def fetch_coins():
    """Fetch cryptocurrency data from multiple sources"""
    coins = []
    
  
    vanry_coin = fetch_vanry_from_binance()
    if vanry_coin:
        coins.append(vanry_coin)
    
   
    other_coins = fetch_coins_from_coingecko()
    

    other_coins = [coin for coin in other_coins if coin['symbol'].lower() != 'vanry']
  
    coins.extend(other_coins)
    
    return coins

@st.cache_data(ttl=300)
def fetch_chart_data_binance(symbol='VANRYUSDT', interval='1h', limit=168):
    """Fetch chart data from Binance (7 days = 168 hours)"""
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
       
        prices = [[candle[0], float(candle[4])] for candle in data]  
        return prices
    except Exception as e:
        st.error(f"Error fetching chart data: {str(e)}")
        return []

@st.cache_data(ttl=300)
def fetch_chart_data_coingecko(coin_id):
    """Fetch 7-day price chart data from CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': 'usd',
        'days': 7
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['prices']
    except Exception as e:
        st.error(f"Error fetching chart data: {str(e)}")
        return []

def format_price(price):
    """Format price based on value"""
    if price < 0.01:
        return f"${price:.6f}"
    elif price < 1:
        return f"${price:.4f}"
    else:
        return f"${price:,.2f}"

def format_market_cap(market_cap):
    """Format market cap with abbreviations"""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    else:
        return f"${market_cap:,.0f}"

def display_coin_detail(coin):
    """Display detailed view of a cryptocurrency"""
    col1, col2 = st.columns([1, 6])
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.selected_coin = None
            st.rerun()
    
    with col2:
        title = f"{coin['name']} ({coin['symbol'].upper()})"
        if coin.get('source') == 'binance':
            title += " - VANRY/USDT on Binance"
        st.markdown(f"<h1>{title}</h1>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Current Price**")
        st.markdown(f"<h2>{format_price(coin['current_price'])}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**24h Change**")
        change = coin.get('price_change_percentage_24h')
        if change is not None:
            color_class = "positive" if change > 0 else "negative"
            arrow = "↑" if change > 0 else "↓"
            st.markdown(f'<h2 class="{color_class}">{arrow} {abs(change):.2f}%</h2>', unsafe_allow_html=True)
        else:
            st.markdown('<h2 style="color: gray;">N/A</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Market Cap**")
        if coin['market_cap'] > 0:
            st.markdown(f"<h2>{format_market_cap(coin['market_cap'])}</h2>", unsafe_allow_html=True)
        else:
            st.markdown('<h2 style="color: gray;">N/A</h2>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Rank**")
        st.markdown(f"<h2>#{coin['market_cap_rank']}</h2>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Additional metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("24h High", format_price(coin['high_24h']))
    
    with col2:
        st.metric("24h Low", format_price(coin['low_24h']))
    
    with col3:
        st.metric("Volume", format_market_cap(coin['total_volume']))
    
    with col4:
        if coin.get('circulating_supply', 0) > 0:
            st.metric("Circulating Supply", f"{coin.get('circulating_supply', 0):,.0f}")
        else:
            st.metric("Circulating Supply", "N/A")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chart
    st.markdown("### 7-Day Price Chart")
    
    with st.spinner("Loading chart data..."):
        if coin.get('source') == 'binance':
            chart_data = fetch_chart_data_binance()
        else:
            chart_data = fetch_chart_data_coingecko(coin['id'])
    
    if chart_data:
        df = pd.DataFrame(chart_data, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        fig = go.Figure()
        
        change = coin.get('price_change_percentage_24h', 0)
        color = '#10b981' if change > 0 else '#ef4444'
        
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['price'],
            mode='lines',
            name='Price',
            line=dict(color=color, width=3),
            fill='tozeroy',
            fillcolor=f'rgba({"16, 185, 129" if color == "#10b981" else "239, 68, 68"}, 0.1)'
        ))
        
        fig.update_layout(
            template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
            height=500,
            hovermode='x unified',
            showlegend=False,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            font=dict(size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)

def display_coin_list(coins, search_term, filter_option):
    """Display list of cryptocurrencies"""
    
    filtered_coins = coins
    
    if search_term:
        filtered_coins = [
            coin for coin in filtered_coins
            if search_term.lower() in coin['name'].lower() or 
               search_term.lower() in coin['symbol'].lower()
        ]
    
    if filter_option == "Gainers":
        filtered_coins = [coin for coin in filtered_coins if coin.get('price_change_percentage_24h') is not None and coin['price_change_percentage_24h'] > 0]
        filtered_coins.sort(key=lambda x: x.get('price_change_percentage_24h', 0), reverse=True)
    elif filter_option == "Losers":
        filtered_coins = [coin for coin in filtered_coins if coin.get('price_change_percentage_24h') is not None and coin['price_change_percentage_24h'] < 0]
        filtered_coins.sort(key=lambda x: x.get('price_change_percentage_24h', 0))
    
 
    if not filtered_coins:
        st.info("No cryptocurrencies found matching your criteria.")
        return
    
    for idx, coin in enumerate(filtered_coins):
        is_vanry = coin.get('source') == 'binance' and coin['symbol'].lower() == 'vanry'
        
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 0.5, 2, 2, 1.5])
            
            with col1:
                st.markdown(f"**#{coin['market_cap_rank']}**")
            
            with col2:
                st.image(coin['image'], width=40)
            
            with col3:
                name_html = f"**{coin['name']}**"
                if is_vanry:
                    name_html += '<span class="vanry-badge">VANRY/USDT</span>'
                st.markdown(name_html, unsafe_allow_html=True)
                st.markdown(f"<small>{coin['symbol'].upper()}</small>", unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"**{format_price(coin['current_price'])}**")
                if coin['market_cap'] > 0:
                    st.markdown(f"<small>{format_market_cap(coin['market_cap'])}</small>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<small>Volume: {format_market_cap(coin['total_volume'])}</small>", unsafe_allow_html=True)
            
            with col5:
                change = coin.get('price_change_percentage_24h')
                if change is not None:
                    color_class = "positive" if change > 0 else "negative"
                    arrow = "↑" if change > 0 else "↓"
                    st.markdown(f'<div class="{color_class}" style="font-size: 18px; text-align: center;">{arrow} {abs(change):.2f}%</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div style="font-size: 18px; text-align: center; color: gray;">N/A</div>', unsafe_allow_html=True)
                
                if st.button("View Details", key=f"btn_{coin['id']}_{idx}", use_container_width=True):
                    st.session_state.selected_coin = coin
                    st.rerun()
            
            st.markdown("---")


def main():
    
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        st.title("💰 Crypto Tracker")
        st.markdown("Real-time cryptocurrency prices powered by Binance & CoinGecko")
    
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col3:
        mode_icon = "☀️" if st.session_state.dark_mode else "🌙"
        if st.button(f"{mode_icon} Mode", use_container_width=True):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    
    
    if st.session_state.selected_coin:
        display_coin_detail(st.session_state.selected_coin)
        return
    
    
    with st.spinner("Loading cryptocurrency data..."):
        coins = fetch_coins()
        st.session_state.coins_data = coins
    
    if not coins:
        st.error("Failed to load cryptocurrency data. Please try again later.")
        return
    
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search cryptocurrencies", placeholder="Search by name or symbol...")
    
    with col2:
        filter_option = st.selectbox("Filter", ["All", "Gainers", "Losers"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    display_coin_list(coins, search_term, filter_option)
    
    
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "VANRY data from Binance | Other coins from CoinGecko | Updated every minute"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()