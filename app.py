from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd
import ta

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development purposes)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)



# Model for the request body
class MarketRequest(BaseModel):
    symbol: str

# Fetch historical data using yfinance
def fetch_data(symbol: str, interval: str, period: str):
    try:
        data = yf.download(tickers=symbol, interval=interval, period=period)
        if data.empty:
            raise ValueError(f"No data found for {symbol} with interval {interval}")

        # Flatten the multi-index columns
        data.columns = ['_'.join(col).strip() for col in data.columns.values]


        return data
    except Exception as e:
        print(f"Failed to download data for {symbol}: {e}")
        return pd.DataFrame()

# Determine market direction using a combination of Moving Averages and RSI
def market_direction(data: pd.DataFrame, symbol: str):
    close_col = f'Close_{symbol}'

    # Check if the 'Close' column for the symbol exists
    if close_col not in data.columns:
        return "No Close Data Available"

    # Drop rows where the 'Close' column for the symbol is NaN
    data = data.dropna(subset=[close_col])

    # Ensure there is sufficient data for calculating indicators
    if len(data) < 50:
        return "Insufficient Data for Indicators"

    # Calculate Moving Averages and RSI
    try:
        data['SMA_20'] = ta.trend.sma_indicator(data[close_col], window=20, fillna=True)
        data['SMA_50'] = ta.trend.sma_indicator(data[close_col], window=50, fillna=True)
        data['RSI'] = ta.momentum.rsi(data[close_col], window=14, fillna=True)
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return "Indicator Calculation Error"

    # Determine market direction based on SMA and RSI values
    sma_20 = data['SMA_20'].iloc[-1]
    sma_50 = data['SMA_50'].iloc[-1]
    rsi = data['RSI'].iloc[-1]

    if sma_20 > sma_50 and rsi < 70:
        return "Uptrend"
    elif sma_20 < sma_50 and rsi > 30:
        return "Downtrend"
    else:
        return "Sideways"

# Analyze market for multiple intervals
@app.post("/analyze_market")
async def analyze_market(request: MarketRequest):
    symbol = request.symbol.upper()
    intervals = {
        '1d': '1y',  # Daily interval with 1-year period
        '1h': '1mo',  # Hourly interval with 1-month period
        '30m': '1mo',  # 30-minute interval with 1-month period
        '15m': '5d',  # 15-minute interval with 5-day period
        '5m': '5d',  # 5-minute interval with 5-day period
        '1m': '5d'  # 1-minute interval with 5-day period
    }

    market_analysis = {}

    for interval, period in intervals.items():
        print(f"symbol:{symbol} | interval: {interval} | period: {period}")
        data = fetch_data(symbol, interval, period)
        # print(f"data: {data}")

        if data.empty or f'Close_{symbol}' not in data.columns:
            direction = "Data Unavailable or Incomplete"
        else:
            direction = market_direction(data, symbol)

        market_analysis[interval] = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{direction}"

    return market_analysis

# Root endpoint for status check
@app.get("/")
async def root():
    return {"message": "Market Analysis API is running"}

