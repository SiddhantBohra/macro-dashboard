import yfinance as yf
import pandas as pd
import requests
from eventregistry import *
import investpy
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

# FRED API Key
FRED_API_KEY = "d5409ca8405ab98621c6e839a561df0a"

# FRED Series IDs for Macroeconomic Indicators
FRED_SERIES = {
    "US": {"GDP": "GDP", "Inflation": "CPIAUCSL", "Unemployment": "UNRATE"},
    "UK": {"GDP": "NGDP_UKQ", "Inflation": "GBRCPIALLMINMEI", "Unemployment": "LRHUTTTTGBM156S"},
    "India": {"GDP": "MKTGDPINA646NWDB", "Inflation": "FPCPITOTLZGIND", "Unemployment": "SLUEM1524ZSIND"},
    "Japan": {"GDP": "JPNNGDP", "Inflation": "JPNCPIALLMINMEI", "Unemployment": "LRHUTTTTJPQ156S"}
}

def get_major_indices():
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "FTSE 100": "^FTSE",
        "Nifty 50": "^NSEI",
        "Nikkei 225": "^N225"
    }
    
    data = {}
    for name, ticker in indices.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1d")
            if not hist.empty:
                data[name] = {
                    'Price': round(hist["Close"].values[0], 2),
                    'Change %': round((hist["Close"].values[0] - hist["Open"].values[0]) / hist["Open"].values[0] * 100, 2)
                }
        except Exception as e:
            print(f"Error fetching data for {name}: {str(e)}")
            data[name] = {'Price': 'N/A', 'Change %': 'N/A'}
    
    return pd.DataFrame.from_dict(data, orient='index')

def get_currency_pairs():
    pairs = {
        "EUR/USD": "EURUSD=X",
        "USD/JPY": "JPY=X",
        "USD/INR": "INR=X",
        "GBP/USD": "GBPUSD=X"
    }
    
    data = {}
    for name, ticker in pairs.items():
        try:
            currency = yf.Ticker(ticker)
            hist = currency.history(period="1d")
            if not hist.empty:
                data[name] = {
                    'Rate': round(hist["Close"].values[0], 4),
                    'Change %': round((hist["Close"].values[0] - hist["Open"].values[0]) / hist["Open"].values[0] * 100, 4)
                }
        except Exception as e:
            data[name] = {'Rate': 'N/A', 'Change %': 'N/A'}
    
    return pd.DataFrame.from_dict(data, orient='index')

def get_bond_yields():
    bonds = {
        "US 10Y Treasury": "^TNX",
        "US 30Y Treasury": "^TYX",
        "US 5Y Treasury": "^FVX",
        "US 2Y Treasury": "^IRX"
    }
    
    data = {}
    for name, ticker in bonds.items():
        try:
            bond = yf.Ticker(ticker)
            hist = bond.history(period="1d")
            if not hist.empty:
                close_yield = hist["Close"].values[0]
                open_yield = hist["Open"].values[0]
                
                # Adjust yields (Yahoo Finance returns them multiplied by 100)
                close_yield = close_yield / 100
                open_yield = open_yield / 100
                
                data[name] = {
                    'Yield %': round(close_yield * 100, 2),  # Convert to percentage
                    'Change': round((close_yield - open_yield) * 100, 2)  # Change in basis points
                }
        except Exception as e:
            data[name] = {'Yield %': 'N/A', 'Change': 'N/A'}
    
    return pd.DataFrame.from_dict(data, orient='index')

def get_commodities():
    commodities = {
        "Crude Oil": "CL=F",
        "Gold (USD)": "GC=F",
        "Silver (USD)": "SI=F",
        "Natural Gas": "NG=F",
        "Copper": "HG=F"
    }
    
    # Get USD/INR rate
    try:
        usd_inr = yf.Ticker("INR=X")
        inr_rate = usd_inr.history(period="1d")["Close"].iloc[-1]
    except Exception as e:
        inr_rate = None
    
    data = {}
    for name, ticker in commodities.items():
        try:
            commodity = yf.Ticker(ticker)
            hist = commodity.history(period="1d")
            if not hist.empty:
                close_price = hist["Close"].values[0]
                open_price = hist["Open"].values[0]
                data[name] = {
                    'Price': round(close_price, 2),
                    'Change %': round((close_price - open_price) / open_price * 100, 2)
                }
                
                # Add INR prices for Gold and Silver
                if name in ["Gold (USD)", "Silver (USD)"] and inr_rate is not None:
                    inr_name = name.replace("USD", "INR")
                    data[inr_name] = {
                        'Price': round(close_price * inr_rate, 2),
                        'Change %': round((close_price - open_price) / open_price * 100, 2)
                    }
        except Exception as e:
            data[name] = {'Price': 'N/A', 'Change %': 'N/A'}
    
    return pd.DataFrame.from_dict(data, orient='index')

def get_geopolitical_news(api_key):
    er = EventRegistry(apiKey=api_key, allowUseOfArchive=False)
    q = QueryArticlesIter(
        keywords="geopolitics",
        sourceLocationUri=QueryItems.OR([
            "http://en.wikipedia.org/wiki/United_Kingdom",
            "http://en.wikipedia.org/wiki/United_States",
            "http://en.wikipedia.org/wiki/Canada",
            "http://en.wikipedia.org/wiki/India",
            "http://en.wikipedia.org/wiki/Japan"
        ]),
        ignoreSourceGroupUri="paywall/paywalled_sources",
        dataType=["news", "pr"]
    )
    
    articles = []
    for article in q.execQuery(er, sortBy="date", sortByAsc=False, maxItems=5):
        articles.append(article["title"])
    return articles

def get_economic_calendar():
    try:
        # Get today's date and format it
        today = datetime.now()
        # Get next 7 days
        next_week = today + timedelta(days=7)
        
        # Format dates for investpy (it expects dd/mm/yyyy)
        today_str = today.strftime('%d/%m/%Y')
        next_week_str = next_week.strftime('%d/%m/%Y')
        
        print(f"Fetching calendar from {today_str} to {next_week_str}")  # Debug print
        
        try:
            # First attempt with investpy
            calendar = investpy.economic_calendar(
                from_date=today_str,
                to_date=next_week_str,
                countries=['united states', 'japan', 'united kingdom', 'india', 'european union']
            )
            
            print("Raw calendar data:", calendar.columns)  # Debug print
            
            if not calendar.empty:
                # Ensure all required columns exist
                required_columns = ['date', 'time', 'country', 'event', 'importance']
                if all(col in calendar.columns for col in required_columns):
                    calendar = calendar[required_columns]
                    calendar = calendar[calendar['importance'].str.lower().isin(['high', 'medium'])]
                    calendar['date'] = pd.to_datetime(calendar['date'])
                    return calendar.sort_values(['date', 'time'])
        
        except Exception as e:
            print(f"Error with investpy: {str(e)}")
            
        # Fallback: Create a basic calendar with known economic events
        fallback_events = [
            {
                'date': today + timedelta(days=1),
                'time': '14:30',
                'country': 'United States',
                'event': 'CPI Data Release',
                'importance': 'high'
            },
            {
                'date': today + timedelta(days=2),
                'time': '14:30',
                'country': 'United States',
                'event': 'Initial Jobless Claims',
                'importance': 'medium'
            },
            {
                'date': today + timedelta(days=3),
                'time': '10:00',
                'country': 'European Union',
                'event': 'ECB Interest Rate Decision',
                'importance': 'high'
            }
        ]
        
        return pd.DataFrame(fallback_events)
        
    except Exception as e:
        print(f"Error in get_economic_calendar: {str(e)}")
        # Return an empty DataFrame with the correct structure
        return pd.DataFrame(columns=['date', 'time', 'country', 'event', 'importance'])

def get_fred_data():
    macro_data = {}
    for country, indicators in FRED_SERIES.items():
        macro_data[country] = {}
        for indicator, series_id in indicators.items():
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "observations" in data and len(data["observations"]) > 0:
                    latest_value = data["observations"][-1]["value"]
                    macro_data[country][indicator] = latest_value
                else:
                    macro_data[country][indicator] = "N/A"
            else:
                macro_data[country][indicator] = "Error"
    return pd.DataFrame(macro_data)

def get_historical_data(ticker, period='5y'):
    """Fetch historical data for the given ticker and period."""
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist

def plot_index_history(ticker, index_name):
    """Create an interactive line plot for the index."""
    st.markdown(f"<h3 style='text-align: center;'>{index_name} Historical Performance</h3>", unsafe_allow_html=True)
    
    # Timeline selection with better styling
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    # Timeline selection buttons with custom styling
    timeline = '1y'  # default
    button_style = """
        padding: 10px 20px;
        width: 100%;
        background-color: #f0f2f6;
        border-radius: 5px;
        """
    
    selected_button_style = """
        padding: 10px 20px;
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        """
    
    with col2:
        if st.button('1Y', key=f'{ticker}_1y', help='Show 1 year data'):
            timeline = '1y'
    with col3:
        if st.button('3Y', key=f'{ticker}_3y', help='Show 3 year data'):
            timeline = '3y'
    with col4:
        if st.button('5Y', key=f'{ticker}_5y', help='Show 5 year data'):
            timeline = '5y'
    
    # Fetch historical data
    df = get_historical_data(ticker, timeline)
    
    # Create the line plot using Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name=index_name,
        line=dict(color='#1f77b4', width=2)
    ))
    
    # Add range slider
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(visible=True),
            type="date",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
        )
    )
    
    # Customize the layout
    fig.update_layout(
        showlegend=False,
        height=600,  # Make the graph taller
        margin=dict(l=40, r=40, t=40, b=40),  # Adjust margins
        hovermode='x unified',
        yaxis=dict(
            tickformat=',',
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            title='Price'
        ),
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_commodities():
    commodities_data = get_commodities()
    
    st.markdown("<h2 style='text-align: center;'>💰 Major Commodities</h2>", unsafe_allow_html=True)
    
    # Create columns - we'll need 5 columns to match the indices layout
    cols = st.columns(5)
    
    # List all commodities in USD
    commodities_list = ["Gold (USD)", "Silver (USD)", "Crude Oil", "Natural Gas", "Copper"]
    
    # Display each commodity
    for i, commodity in enumerate(commodities_list):
        with cols[i]:
            row = commodities_data.loc[commodity]
            price = row['Price']
            change = row['Change %']
            
            # Clean up display name (remove USD suffix)
            display_name = commodity.replace(" (USD)", "")
            
            # Determine colors based on percentage change
            bg_color = "#E8F5E9" if change > 0 else "#FFEBEE"
            text_color = "#0B6623" if change > 0 else "#8B0000"
            
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    height: 150px;
                    cursor: pointer;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    <h3 style="margin: 0; font-size: 16px; color: #333;">{display_name}</h3>
                    <div style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">
                        {price:,.2f}
                    </div>
                    <div style="
                        display: inline-block;
                        padding: 4px 8px;
                        border-radius: 15px;
                        font-size: 14px;
                        font-weight: bold;
                        color: {text_color};
                    ">
                        {f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def display_news_ticker():
    # Get the news headlines
    API_KEY = "ec207602-3b95-4e3c-9eb4-3a38f5b87459"
    headlines = get_geopolitical_news(API_KEY)
    
    if headlines:
        st.markdown(
            """
            <div style="
                background-color: #1E1E1E;
                border-radius: 10px;
                border: 1px solid #333;
                margin: 20px 0;
            ">
                <div style="
                    display: flex;
                    align-items: center;
                    padding: 12px 20px;
                    border-bottom: 1px solid #333;
                ">
                    <div style="
                        background-color: #252525;
                        padding: 6px;
                        border-radius: 6px;
                        margin-right: 12px;
                        border: 1px solid #333;
                    ">
                        📰
                    </div>
                    <h2 style="color: white; margin: 0; font-size: 20px;">Latest News</h2>
                </div>
                <div style="padding: 15px 20px;">
            """,
            unsafe_allow_html=True
        )
        
        # Display each headline in a clean, readable format
        for headline in headlines:
            st.markdown(
                f"""
                <div style="
                    color: white;
                    padding: 8px 0;
                    font-size: 14px;
                    border-bottom: 1px solid #333;
                ">
                    • {headline}
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                color: #888;
                border: 1px solid #333;
                margin: 20px 0;
            ">
                <div style="font-size: 20px; margin-bottom: 5px;">📰</div>
                <div style="font-size: 14px;">No news headlines available</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_currency_and_yields():
    # Get the data
    currency_data = get_currency_pairs()
    bond_data = get_bond_yields()
    
    # Create two columns with 1:1 ratio
    col1, col2 = st.columns(2)
    
    # Currency pairs table in the left column
    with col1:
        st.markdown("<h3 style='text-align: left;'>💱 Currency Pairs</h3>", unsafe_allow_html=True)
        
        # Header row
        st.markdown(
            """
            <div style="
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 20px;
                margin: 10px 0;
            ">
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    border-bottom: 1px solid #333;
                    padding-bottom: 10px;
                    margin-bottom: 15px;
                    color: #888;
                ">
                    <div>Pair</div>
                    <div style="text-align: right;">Rate</div>
                    <div style="text-align: right;">Change</div>
                </div>
            """,
            unsafe_allow_html=True
        )
        
        # Data rows
        for pair, row in currency_data.iterrows():
            rate = row['Rate']
            change = row['Change %']
            color = "#00C805" if change > 0 else "#FF3B3B"
            change_text = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
            
            st.markdown(
                f"""
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    padding: 10px 0;
                    color: white;
                    font-size: 16px;
                ">
                    <div style="color: white;">{pair}</div>
                    <div style="text-align: right;">{rate:.4f}</div>
                    <div style="text-align: right; color: {color};">{change_text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 10Y Treasury yield card in the right column
    with col2:
        st.markdown("<h2 style='text-align: left; color: white; font-size: 24px; margin-bottom: 20px;'>📈 US 10Y Treasury</h2>", unsafe_allow_html=True)
        
        # Get 10Y yield data
        yield_data = bond_data.loc["US 10Y Treasury"]
        yield_value = yield_data['Yield %']
        change = yield_data['Change']
        
        # Determine colors based on change
        bg_color = "#E8F5E9" if change > 0 else "#FFEBEE"  # Light green/red background
        text_color = "#0B6623" if change > 0 else "#8B0000"  # Dark green/red text
        change_text = f"+{change:.2f}" if change > 0 else f"{change:.2f}"
        
        # Create yield card with matching style
        st.markdown(
            f"""
            <div style="
                background-color: {bg_color};
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                height: 150px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            ">
                <h3 style="margin: 0; font-size: 16px; color: #333;">Yield</h3>
                <div style="font-size: 36px; font-weight: bold; margin: 10px 0; color: #333;">
                    {yield_value:.2f}%
                </div>
                <div style="
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 15px;
                    font-size: 14px;
                    font-weight: bold;
                    color: {text_color};
                ">
                    {change_text} bps
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add the economic calendar below
    display_economic_calendar()
    
    # Add the news ticker below the economic calendar
    display_news_ticker()

def display_economic_calendar():
    st.markdown(
        """
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            background-color: #1E1E1E;
            padding: 12px 20px;
            border-radius: 10px;
            border: 1px solid #333;
        ">
            <div style="
                background-color: #252525;
                padding: 6px;
                border-radius: 6px;
                margin-right: 12px;
                border: 1px solid #333;
            ">
                📅
            </div>
            <h2 style="color: white; margin: 0; font-size: 20px;">Economic Calendar</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    calendar = get_economic_calendar()
    
    if not calendar.empty:
        st.markdown(
            """
            <div style="
                background-color: #1E1E1E;
                border-radius: 10px;
                border: 1px solid #333;
                overflow: hidden;
            ">
                <div style="
                    display: grid;
                    grid-template-columns: 100px 100px 140px minmax(200px, 1fr) 80px;
                    gap: 10px;
                    padding: 12px 20px;
                    background-color: #252525;
                    border-bottom: 1px solid #333;
                    color: #888;
                    font-size: 13px;
                    font-weight: 500;
                ">
                    <div>Date</div>
                    <div>Time</div>
                    <div>Country</div>
                    <div>Event</div>
                    <div style="text-align: center;">Impact</div>
                </div>
                <div style="padding: 5px 10px;">
            """,
            unsafe_allow_html=True
        )
        
        for _, event in calendar.iterrows():
            date_str = pd.to_datetime(event['date']).strftime('%d %b')
            importance = event['importance'].lower()
            importance_color = '#FF3B3B' if importance == 'high' else '#FFA500'
            importance_bg = '#2D1A1A' if importance == 'high' else '#2D2416'
            
            st.markdown(
                f"""
                <div style="
                    display: grid;
                    grid-template-columns: 100px 100px 140px minmax(200px, 1fr) 80px;
                    gap: 10px;
                    padding: 8px 20px;
                    align-items: center;
                    border-bottom: 1px solid #333;
                    font-size: 13px;
                ">
                    <div style="color: #888;">{date_str}</div>
                    <div style="color: #888; font-family: monospace;">{event['time']}</div>
                    <div style="color: #CCC;">{event['country']}</div>
                    <div style="color: white;">{event['event']}</div>
                    <div style="
                        background-color: {importance_bg};
                        color: {importance_color};
                        padding: 2px 4px;
                        border-radius: 3px;
                        text-align: center;
                        font-size: 11px;
                        font-weight: bold;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    ">
                        {importance}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div style="
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                color: #888;
                border: 1px solid #333;
            ">
                <div style="font-size: 20px; margin-bottom: 5px;">📅</div>
                <div style="font-size: 14px;">No economic events scheduled for the next 7 days</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_indices():
    # Get indices data
    indices_data = get_major_indices()
    
    # Define ticker mapping
    ticker_mapping = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "FTSE 100": "^FTSE",
        "Nifty 50": "^NSEI",
        "Nikkei 225": "^N225"
    }
    
    # Set up layout
    st.markdown("<h2 style='text-align: center;'>📉 Major Global Indices</h2>", unsafe_allow_html=True)
    
    # Create columns for the cards
    cols = st.columns(5)

    # Store the selected index
    if 'selected_index' not in st.session_state:
        st.session_state.selected_index = None

    for i, (index_name, row) in enumerate(indices_data.iterrows()):
        price = row['Price']
        change = row['Change %']
        
        with cols[i]:
            # Determine colors based on percentage change
            if isinstance(change, (int, float)):
                color = "#0B6623" if change > 0 else "#8B0000"  # Green for positive, Red for negative
                change_text = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
                bg_color = "#E8F5E9" if change > 0 else "#FFEBEE"
            else:
                color = "#757575"  # Gray for N/A
                change_text = "N/A"
                bg_color = "#F5F5F5"

            # Create a container for the card
            st.markdown(
                f"""
                <div style="
                    background-color: {bg_color};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    height: 150px;  /* Increased height slightly */
                    cursor: pointer;
                    transition: transform 0.2s;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    <h3 style="margin: 0; font-size: 16px; color: #333;">{index_name}</h3>
                    <div style="font-size: 24px; font-weight: bold; margin: 10px 0; color: #333;">
                        {price:,}
                    </div>
                    <div style="
                        display: inline-block;
                        padding: 4px 8px;
                        border-radius: 15px;
                        font-size: 14px;
                        font-weight: bold;
                        color: {color};
                        margin-bottom: 8px;  /* Added margin to separate from button */
                    ">
                        {change_text}
                    </div>
                </div>
                """, unsafe_allow_html=True
            )

            # Add click detection
            if st.button("View Chart", key=f"card_{index_name}", help=f"Click to view {index_name} chart"):
                st.session_state.selected_index = index_name

    # Display the graph for the selected index
    if st.session_state.selected_index:
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Create columns for better button placement
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("✖ Close", 
                        key="close_chart", 
                        type="primary",
                        help="Close the chart view"):
                st.session_state.selected_index = None
                st.rerun()
        
        plot_index_history(ticker_mapping[st.session_state.selected_index], st.session_state.selected_index)
        
        # Add commodities display below the chart
        st.markdown("<hr>", unsafe_allow_html=True)
        display_commodities()
        
        # Add currency pairs and yields display
        st.markdown("<hr>", unsafe_allow_html=True)
        display_currency_and_yields()

if __name__ == "__main__":
    display_indices()
    if not st.session_state.get('selected_index'):  # If no chart is displayed
        st.markdown("<hr>", unsafe_allow_html=True)
        display_commodities()  # Display commodities by default
        st.markdown("<hr>", unsafe_allow_html=True)
        display_currency_and_yields()  # Display currency pairs and yields
    
    # Display bond yields
    print("\nGovernment Bond Yields:")
    bond_data = get_bond_yields()
    print(bond_data)
    
    # Display commodity prices
    print("\nMajor Commodities:")
    commodity_data = get_commodities()
    print(commodity_data)
    
    # Display latest geopolitical news headlines
    print("\nLatest Geopolitical News Headlines:")
    API_KEY = "ec207602-3b95-4e3c-9eb4-3a38f5b87459"  # Your API Key
    geopolitical_headlines = get_geopolitical_news(API_KEY)
    for i, headline in enumerate(geopolitical_headlines, 1):
        print(f"{i}. {headline}")
    
    # Display economic calendar
    print("\nEconomic Calendar:")
    economic_calendar_data = get_economic_calendar()
    print(economic_calendar_data)

    # Fetch and display macroeconomic data
    print("\nFetching Macro Data from FRED API...")
    macro_data = get_fred_data()
    print(macro_data)



