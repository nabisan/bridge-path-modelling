"""
Schrödinger Bridge solver using Gaussian approximation
"""

import numpy as np
import pandas as pd
from scipy import stats
import yaml
from pathlib import Path


class SchrodingerBridge:
    """Compute entropy-minimizing bridge between distributions"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.n_steps = self.config['bridge']['time_steps']
        self.T = 1.0  # Normalized time
        
        # Results storage
        self.t_grid = None
        self.mu_t = None
        self.sigma_t = None
        self.drift = None
        self.volatility = None
    
    def fit(self, open_returns, close_returns):
        """
        Compute Schrödinger Bridge between open and close distributions
        
        Using Gaussian approximation for tractability
        """
        print("\n🌉 Computing Schrödinger Bridge...")
        
        # Fit Gaussian to marginals
        self.mu_0 = open_returns.mean()
        self.sigma_0 = open_returns.std()
        self.mu_T = close_returns.mean()
        self.sigma_T = close_returns.std()
        
        print(f"Initial (t=0): μ={self.mu_0:.6f}, σ={self.sigma_0:.6f}")
        print(f"Final (t=T):   μ={self.mu_T:.6f}, σ={self.sigma_T:.6f}")
        
        # Time grid
        self.t_grid = np.linspace(0, self.T, self.n_steps)
        
        # Entropy-minimizing bridge (linear interpolation for Gaussians)
        self.mu_t = self.mu_0 + (self.mu_T - self.mu_0) * self.t_grid
        self.sigma_t = np.sqrt(self.sigma_0**2 + (self.sigma_T**2 - self.sigma_0**2) * self.t_grid)
        
        # Estimate drift from Fokker-Planck
        dt = self.T / (self.n_steps - 1)
        drift_t = np.diff(self.mu_t) / dt
        self.drift = drift_t.mean()
        self.volatility = self.sigma_t.mean()
        
        # Mean reversion strength
        self.reversion_strength = abs(self.drift) / self.volatility
        
        print(f"\n📊 Bridge parameters:")
        print(f"   Drift: {self.drift:.6f}")
        print(f"   Volatility: {self.volatility:.6f}")
        print(f"   Reversion strength: {self.reversion_strength:.4f}")
        
        return self
    
    def get_bridge_path(self):
        """Return bridge evolution parameters"""
        return {
            't': self.t_grid,
            'mu': self.mu_t,
            'sigma': self.sigma_t,
            'drift': self.drift,
            'volatility': self.volatility,
            'reversion_strength': self.reversion_strength
        }
    
    def save_results(self):
        """Save bridge results to CSV"""
        results_path = Path(self.config['paths']['results_tables'])
        results_path.mkdir(parents=True, exist_ok=True)
        
        # Bridge path
        bridge_df = pd.DataFrame({
            'time': self.t_grid,
            'mean': self.mu_t,
            'volatility': self.sigma_t
        })
        bridge_df.to_csv(results_path / 'bridge_path.csv', index=False)
        
        # Summary stats
        summary = pd.DataFrame({
            'Metric': ['Initial mean', 'Final mean', 'Initial vol', 'Final vol',
                      'Drift', 'Volatility', 'Reversion strength'],
            'Value': [self.mu_0, self.mu_T, self.sigma_0, self.sigma_T,
                     self.drift, self.volatility, self.reversion_strength]
        })
        summary.to_csv(results_path / 'summary_stats.csv', index=False)
        
        print(f"✅ Results saved to {results_path}")


if __name__ == "__main__":
    # Test bridge computation
    from data_loader import DataLoader
    
    loader = DataLoader()
    open_ret, close_ret = loader.load_processed_data()
    
    bridge = SchrodingerBridge()
    bridge.fit(open_ret, close_ret)
    bridge.save_results()
    
    print("\n✅ Bridge computation complete!")

