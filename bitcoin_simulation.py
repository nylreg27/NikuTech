import numpy as np
import pandas as pd

def simulate_bitcoin_prices(days=60, start_price=60000, mu=0.0002, sigma=0.04):
    """
    Simulates Bitcoin price data using Geometric Brownian Motion.
    mu: daily drift
    sigma: daily volatility
    """
    np.random.seed(42)  # For reproducibility
    dt = 1
    prices = [start_price]
    for _ in range(1, days):
        price = prices[-1] * np.exp((mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * np.random.normal())
        prices.append(price)

    dates = pd.date_range(start='2023-01-01', periods=days)
    df = pd.DataFrame({'Date': dates, 'Price': prices})
    return df

def calculate_moving_averages(df):
    """
    Calculates 7-day and 30-day moving averages.
    """
    df['MA7'] = df['Price'].rolling(window=7).mean()
    df['MA30'] = df['Price'].rolling(window=30).mean()
    return df

def run_trading_simulation(df, initial_capital=10000.0):
    """
    Implements a 'Golden Cross' trading algorithm.
    Buy when MA7 > MA30, Sell when MA7 < MA30.
    """
    capital = initial_capital
    position = 0.0  # Amount of BTC held
    ledger = []

    for i in range(len(df)):
        date = df.iloc[i]['Date']
        price = df.iloc[i]['Price']
        ma7 = df.iloc[i]['MA7']
        ma30 = df.iloc[i]['MA30']

        # Skip days where MAs are not yet available
        if pd.isna(ma7) or pd.isna(ma30):
            ledger.append({'Date': date, 'Price': price, 'Action': 'Hold', 'Capital': capital, 'BTC': position})
            continue

        action = 'Hold'
        if ma7 > ma30 and position == 0:
            # Buy
            position = capital / price
            capital = 0.0
            action = 'Buy'
        elif ma7 < ma30 and position > 0:
            # Sell
            capital = position * price
            position = 0.0
            action = 'Sell'

        ledger.append({
            'Date': date,
            'Price': price,
            'Action': action,
            'Capital': capital,
            'BTC': position,
            'Total Value': capital + position * price
        })

    ledger_df = pd.DataFrame(ledger)

    final_price = df.iloc[-1]['Price']
    final_value = capital + position * final_price
    roi = (final_value - initial_capital) / initial_capital * 100

    return ledger_df, final_value, roi

if __name__ == "__main__":
    initial_cap = 10000.0
    df = simulate_bitcoin_prices(60)
    df = calculate_moving_averages(df)

    ledger, final_val, roi = run_trading_simulation(df, initial_capital=initial_cap)

    print("Daily Ledger:")
    print(ledger.to_string(index=False))

    print("\n" + "="*30)
    print(f"Final Portfolio Performance:")
    print(f"Initial Capital: ${initial_cap:,.2f}")
    print(f"Final Portfolio Value: ${final_val:,.2f}")
    print(f"Total ROI: {roi:.2f}%")
    print("="*30)
