import yfinance as yf
import pandas as pd
import ta
import os
import keyboard
import time

# ANSI color codes
RED = '\033[91m'
BLUE = '\033[94m'
WHITE = '\033[97m'
RESET = '\033[0m'

# Fetch historical data using yfinance
def fetch_data(symbol, interval, period):
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
def market_direction(data, symbol):
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

    print(f"sma 20: {sma_20} | sma 50 : {sma_50} | RSI : {rsi}")

    if sma_20 > sma_50 and rsi < 70:
        return "Uptrend"
    elif sma_20 < sma_50 and rsi > 30:
        return "Downtrend"
    else:
        return "Sideways"


# Main function to determine direction across multiple intervals
def analyze_market(symbol):
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
        print(f"Fetching data for {symbol} with interval {interval}...")
        data = fetch_data(symbol, interval, period)

        if data.empty or f'Close_{symbol}' not in data.columns:
            direction = "Data Unavailable or Incomplete"
        else:
            direction = market_direction(data, symbol)

        market_analysis[interval] = direction

    return market_analysis


def clear_screen():
    # Clear the screen based on the operating system
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For macOS and Linux
        os.system('clear')


def main():
    while True:
        clear_screen()
        symbol = input("Enter the pair (e.g., XRP-USD, GOLD-USD) or press 'exit' or 'E' to close the app: ").strip().upper()

        if symbol in ['EXIT', 'E']:
            print("Exiting the app.")
            break

        if not symbol:
            symbol = "gold-usd".upper()  # Default to Gold/USD

        noOfRounds = 0
        while True:
            noOfRounds += 1
            market_directions = analyze_market(symbol)

            # Print market direction for each interval
            print()
            print()
            print("---------------------------------------------------")
            print(f"[{noOfRounds}] | CURRENT TREND FOR {symbol} ")
            print("---------------------------------------------------")
            for interval, direction in market_directions.items():
                if direction == "Downtrend":
                    color = RED
                elif direction == "Uptrend":
                    color = BLUE
                else:
                    color = WHITE
                print(f"\tMarket Direction for {interval}: {color}{direction}{RESET}")

            # Initialize breakout flag
            breakout = False

            # Refresh every 60 seconds or until 'esc' is pressed
            print()
            for remaining in range(60, 0, -1):
                print(f"\r| Refreshing in {remaining}s...", end="")
                time.sleep(1)

                if keyboard.is_pressed('esc'):
                    print("\nReturning to pair selection.")
                    breakout = True
                    break

            if breakout:
                # Reset breakout flag and break out of the current symbol loop
                breakout = False
                break

            # Clear the screen before printing the results
            clear_screen()



# Example Usage
if __name__ == "__main__":
    main()
