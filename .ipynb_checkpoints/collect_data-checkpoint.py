"""
Schrödinger Bridge Data Collection
Collect S&P 500 intraday data for distribution analysis
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("📊 Starting data collection...")
print("="*60)

# Download SPY intraday data (last 30 days)
ticker = yf.Ticker("SPY")

try:
    # Get 1-minute data for past month
    print("Downloading SPY 1-minute data (last 30 days)...")
    data = ticker.history(period="1mo", interval="1m")
    print(f"✅ Downloaded {len(data)} data points")
    
    # Remove timezone info for easier processing
    data.index = data.index.tz_localize(None)
    
    # Compute log returns
    data['returns'] = np.log(data['Close'] / data['Close'].shift(1))
    
    # Add time column
    data['time'] = data.index.time
    data['date'] = data.index.date
    
    # Filter market hours (9:30 AM - 4:00 PM EST)
    market_open = pd.Timestamp('09:30:00').time()
    market_close = pd.Timestamp('16:00:00').time()
    
    data = data[(data['time'] >= market_open) & (data['time'] <= market_close)]
    
    print(f"✅ Filtered to market hours: {len(data)} points")
    
    # Extract opening returns (9:30-9:35 AM window)
    open_window = pd.Timestamp('09:35:00').time()
    open_returns = data[(data['time'] >= market_open) & 
                        (data['time'] <= open_window)]['returns'].dropna()
    
    # Extract closing returns (3:55-4:00 PM window)
    close_start = pd.Timestamp('15:55:00').time()
    close_returns = data[(data['time'] >= close_start) & 
                         (data['time'] <= market_close)]['returns'].dropna()
    
    print(f"\n📈 Distribution Statistics:")
    print(f"Open returns  : N={len(open_returns)}, μ={open_returns.mean():.6f}, σ={open_returns.std():.6f}")
    print(f"Close returns : N={len(close_returns)}, μ={close_returns.mean():.6f}, σ={close_returns.std():.6f}")
    
    # Save data
    open_returns.to_csv('data/open_returns.csv', index=False, header=['returns'])
    close_returns.to_csv('data/close_returns.csv', index=False, header=['returns'])
    data.to_csv('data/spy_intraday_full.csv')
    
    print(f"\n✅ Data saved:")
    print(f"   - data/open_returns.csv ({len(open_returns)} samples)")
    print(f"   - data/close_returns.csv ({len(close_returns)} samples)")
    print(f"   - data/spy_intraday_full.csv ({len(data)} samples)")
    
    print("\n" + "="*60)
    print("🎉 Data collection complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Trying alternative approach...")
    
    # Fallback: use 5-minute intervals
    data = ticker.history(period="1mo", interval="5m")
    data.index = data.index.tz_localize(None)
    data['returns'] = np.log(data['Close'] / data['Close'].shift(1))
    data['time'] = data.index.time
    
    market_open = pd.Timestamp('09:30:00').time()
    market_close = pd.Timestamp('16:00:00').time()
    
    open_returns = data[data['time'] == market_open]['returns'].dropna()
    close_returns = data[data['time'] == market_close]['returns'].dropna()
    
    open_returns.to_csv('data/open_returns.csv', index=False, header=['returns'])
    close_returns.to_csv('data/close_returns.csv', index=False, header=['returns'])
    
    print("✅ Fallback data collection successful (5-min intervals)")

