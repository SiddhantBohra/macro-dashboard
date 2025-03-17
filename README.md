# 📊 Market Finance Quantitative Dashboard

![Dashboard Preview](https://via.placeholder.com/800x400?text=Market+Finance+Dashboard+Preview)

A comprehensive financial markets dashboard built with Streamlit that provides real-time data visualization for global markets, including indices, commodities, currencies, and economic indicators.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-FF4B4B)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🌎 Global Market Indices**: Track major indices like S&P 500, NASDAQ, FTSE 100, Nifty 50, and Nikkei 225
- **📈 Interactive Charts**: View historical performance with adjustable timeframes (1Y, 3Y, 5Y)
- **💰 Commodity Prices**: Monitor prices for Gold, Silver, Crude Oil, Natural Gas, and Copper
- **💱 Currency Pairs**: Track major forex pairs including EUR/USD, USD/JPY, USD/INR, and GBP/USD
- **📝 Bond Yields**: Display US Treasury yields with visual indicators
- **📅 Economic Calendar**: View upcoming economic events with importance indicators
- **📰 Financial News**: Latest geopolitical news headlines relevant to financial markets
- **🌙 Dark Theme**: Optimized for financial market monitoring with a sleek dark interface
- **📊 Macroeconomic Indicators**: GDP, Inflation, and Unemployment data for major economies

## 🖼️ Screenshots

<table>
  <tr>
    <td><img src="https://via.placeholder.com/400x200?text=Indices+View" alt="Indices View"/></td>
    <td><img src="https://via.placeholder.com/400x200?text=Commodities+View" alt="Commodities View"/></td>
  </tr>
  <tr>
    <td><img src="https://via.placeholder.com/400x200?text=Economic+Calendar" alt="Economic Calendar"/></td>
    <td><img src="https://via.placeholder.com/400x200?text=News+Headlines" alt="News Headlines"/></td>
  </tr>
</table>

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- API keys for FRED and Event Registry

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/mf-quant-model.git
cd mf-quant-model
```

2. Create and activate a virtual environment (recommended):
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your API keys:
   - You'll need API keys for:
     - [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html) (for economic data)
     - [Event Registry API](https://eventregistry.org/documentation/api) (for news headlines)
   
   - Create a `.env` file in the project root:
   ```
   FRED_API_KEY=your_fred_api_key_here
   EVENT_REGISTRY_API_KEY=your_event_registry_api_key_here
   ```
   
   - Or update the API keys directly in the dashboard.py file:
   ```python
   # FRED API Key
   FRED_API_KEY = "your_fred_api_key_here"
   
   # In the get_geopolitical_news function
   API_KEY = "your_event_registry_api_key_here"
   ```

## 🖥️ Usage

Run the dashboard with:
```bash
streamlit run dashboard.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

## 📋 Dashboard Sections

### 1. Major Global Indices
- Cards showing current prices and daily changes
- Interactive historical charts with adjustable timeframes
   
### 2. Commodities
- Current prices and daily changes for major commodities
- Gold and Silver prices in both USD and INR
   
### 3. Currency Pairs
- Exchange rates and daily changes for major currency pairs
- Includes EUR/USD, USD/JPY, USD/INR, and GBP/USD
   
### 4. US Treasury Yields
- Current yield and daily change for the US 10Y Treasury
- Visual indicators for yield movements
   
### 5. Economic Calendar
- Upcoming economic events with importance indicators
- Filtered for high and medium importance events
   
### 6. News Headlines
- Latest financial and geopolitical news
- Sourced from Event Registry API

## 📊 Data Sources

- **Market Data**: Yahoo Finance (via yfinance)
- **Economic Data**: Federal Reserve Economic Data (FRED)
- **News Headlines**: Event Registry API
- **Economic Calendar**: Investing.com (via investpy)

## 📦 Dependencies

The dashboard relies on the following main Python libraries:
- `streamlit`: Web application framework
- `yfinance`: Yahoo Finance data
- `pandas`: Data manipulation and analysis
- `plotly`: Interactive visualizations
- `requests`: HTTP requests for API calls
- `eventregistry`: News data API client
- `investpy`: Economic calendar data

See `requirements.txt` for a complete list of dependencies with versions.

## 🔧 Customization

You can customize the dashboard by:

1. **Adding New Indices**: Modify the `indices` dictionary in the `get_major_indices()` function
2. **Adding New Commodities**: Update the `commodities` dictionary in the `get_commodities()` function
3. **Changing Time Periods**: Adjust the timeline options in the `plot_index_history()` function
4. **Modifying UI Colors**: Update the color schemes in the various display functions

## ❓ Troubleshooting

- **Economic Calendar Issues**: If the investpy economic calendar fails, the dashboard will fall back to a basic calendar with known economic events.
- **API Rate Limits**: If you encounter rate limit issues with Yahoo Finance, consider implementing a delay between requests.
- **Missing Data**: If certain data points show as "N/A", check your internet connection or try refreshing the dashboard.

## 🔄 Future Improvements

- Add portfolio tracking functionality
- Implement technical indicators for chart analysis
- Add cryptocurrency market data
- Create alert system for significant market movements
- Implement machine learning-based market predictions

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgements

- Streamlit for the web application framework
- Yahoo Finance for market data
- FRED for economic indicators
- Event Registry for news data
- Investing.com for economic calendar data 