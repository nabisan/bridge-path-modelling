"""
Data loading and preprocessing for intraday returns
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
from pathlib import Path


class DataLoader:
    """Load and preprocess SPY intraday data"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.ticker = self.config['data']['ticker']
        self.weeks_back = self.config['data']['weeks_back']
        self.interval = self.config['data']['interval']
        
        # Create directories
        Path(self.config['paths']['raw_data']).mkdir(parents=True, exist_ok=True)
        Path(self.config['paths']['processed_data']).mkdir(parents=True, exist_ok=True)
    
    def fetch_data(self):
        """Fetch intraday data from Yahoo Finance"""
        print(f"Fetching {self.ticker} data for {self.weeks_back} weeks...")
        
        ticker_obj = yf.Ticker(self.ticker)
        all_data = []
        
        for week in range(self.weeks_back):
            try:
                end_date = datetime.now() - timedelta(days=week*7)
                start_date = end_date - timedelta(days=7)
                
                print(f"  Week {week+1}: {start_date.date()} to {end_date.date()}")
                
                data = ticker_obj.history(start=start_date, end=end_date, interval=self.interval)
                
                if len(data) > 0:
                    all_data.append(data)
                    print(f"    {len(data)} records")
                
            except Exception as e:
                print(f"      Error: {e}")
                continue
        
        if not all_data:
            raise ValueError("No data collected!")
        
        # Combine all weeks
        combined_data = pd.concat(all_data)
        
        # Save raw data
        raw_path = Path(self.config['paths']['raw_data']) / 'spy_intraday_full.csv'
        combined_data.to_csv(raw_path)
        print(f"Saved raw data: {raw_path}")
        
        return combined_data
    
    def process_returns(self, data):
        """Process data to extract open/close returns"""
        print("\n Processing returns...")
        
        # Remove timezone if present
        if hasattr(data.index, 'tz_localize'):
            data.index = data.index.tz_localize(None)
        
        # Compute log returns
        data['returns'] = np.log(data['Close'] / data['Close'].shift(1))
        data['time'] = data.index.time
        
        # Filter market hours
        market_open = pd.Timestamp(self.config['data']['market_open']).time()
        market_close = pd.Timestamp(self.config['data']['market_close']).time()
        data = data[(data['time'] >= market_open) & (data['time'] <= market_close)]
        
        # Extract open returns
        open_window = pd.Timestamp(self.config['data']['open_window']).time()
        open_returns = data[(data['time'] >= market_open) & 
                           (data['time'] <= open_window)]['returns'].dropna()
        
        # Extract close returns
        close_start = pd.Timestamp(self.config['data']['close_start']).time()
        close_returns = data[(data['time'] >= close_start) & 
                            (data['time'] <= market_close)]['returns'].dropna()
        
        # Save processed data
        processed_path = Path(self.config['paths']['processed_data'])
        open_returns.to_csv(processed_path / 'open_returns.csv', index=False, header=['returns'])
        close_returns.to_csv(processed_path / 'close_returns.csv', index=False, header=['returns'])
        
        print(f"Open returns: {len(open_returns)} samples")
        print(f"Close returns: {len(close_returns)} samples")
        
        return open_returns, close_returns
    
    def load_processed_data(self):
        """Load previously processed data"""
        processed_path = Path(self.config['paths']['processed_data'])
        
        open_returns = pd.read_csv(processed_path / 'open_returns.csv')['returns']
        close_returns = pd.read_csv(processed_path / 'close_returns.csv')['returns']
        
        return open_returns, close_returns


if __name__ == "__main__":
    # Test data loading
    loader = DataLoader()
    data = loader.fetch_data()
    open_ret, close_ret = loader.process_returns(data)
    
    print(f"\n Summary:")
    print(f"   Open: μ={open_ret.mean():.6f}, σ={open_ret.std():.6f}")
    print(f"   Close: μ={close_ret.mean():.6f}, σ={close_ret.std():.6f}")

