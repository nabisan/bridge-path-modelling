"""
Improved data collection - get more historical data
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("📊 Improved Data Collection - Multiple Weeks")
print("="*60)

ticker = yf.Ticker("SPY")

# Strategy: Download multiple 7-day chunks
all_open_returns = []
all_close_returns = []

print("Downloading data in weekly chunks...")

for week in range(4):  # Last 4 weeks
    try:
        # Download 7 days at a time (Yahoo limit for 1-min data)
        end_date = datetime.now() - timedelta(days=week*7)
        start_date = end_date - timedelta(days=7)
        
        print(f"\nWeek {week+1}: {start_date.date()} to {end_date.date()}")
        
        data = ticker.history(start=start_date, end=end_date, interval="1m")
        
        if len(data) == 0:
            print(f"  ⚠️ No data for this week, skipping...")
            continue
            
        # Process data
        if hasattr(data.index, 'tz_localize'):
            data.index = data.index.tz_localize(None)
        
        data['returns'] = np.log(data['Close'] / data['Close'].shift(1))
        data['time'] = data.index.time
        
        # Filter market hours
        market_open = pd.Timestamp('09:30:00').time()
        market_close = pd.Timestamp('16:00:00').time()
        
        data = data[(data['time'] >= market_open) & (data['time'] <= market_close)]
        
        # Extract returns
        open_window = pd.Timestamp('09:35:00').time()
        open_ret = data[(data['time'] >= market_open) & 
                       (data['time'] <= open_window)]['returns'].dropna()
        
        close_start = pd.Timestamp('15:55:00').time()
        close_ret = data[(data['time'] >= close_start) & 
                        (data['time'] <= market_close)]['returns'].dropna()
        
        all_open_returns.extend(open_ret.values)
        all_close_returns.extend(close_ret.values)
        
        print(f"  ✅ Got {len(open_ret)} open returns, {len(close_ret)} close returns")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        continue

# Combine all data
open_returns = pd.DataFrame({'returns': all_open_returns})
close_returns = pd.DataFrame({'returns': all_close_returns})

print(f"\n📈 TOTAL Distribution Statistics:")
print(f"Open returns  : N={len(open_returns)}, μ={open_returns['returns'].mean():.6f}, σ={open_returns['returns'].std():.6f}")
print(f"Close returns : N={len(close_returns)}, μ={close_returns['returns'].mean():.6f}, σ={close_returns['returns'].std():.6f}")

# Save
open_returns.to_csv('data/open_returns.csv', index=False)
close_returns.to_csv('data/close_returns.csv', index=False)

print(f"\n✅ Saved to data/ folder")
print("="*60)
print("🎉 Improved data collection complete!")

