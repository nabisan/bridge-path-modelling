"""
Visualization module for Schrödinger Bridge analysis
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
import yaml
from pathlib import Path


class Visualizer:
    """Create professional visualizations for bridge analysis"""
    
    def __init__(self, config_path='config.yaml'):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Set style
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 11
        
        # Ensure output directory exists
        self.figures_path = Path(self.config['paths']['results_figures'])
        self.figures_path.mkdir(parents=True, exist_ok=True)
    
    def plot_distributions(self, open_returns, close_returns):
        """Plot open vs close return distributions"""
        print("\n📊 Creating distribution plots...")
        
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Subplot 1: Overlaid histograms
        axes[0].hist(open_returns, bins=25, density=True, alpha=0.6,
                    color='blue', label='Open (9:30 AM)', edgecolor='black')
        axes[0].hist(close_returns, bins=25, density=True, alpha=0.6,
                    color='orange', label='Close (4:00 PM)', edgecolor='black')
        axes[0].axvline(open_returns.mean(), color='blue', linestyle='--', linewidth=2,
                       label=f'Open μ={open_returns.mean():.5f}')
        axes[0].axvline(close_returns.mean(), color='orange', linestyle='--', linewidth=2,
                       label=f'Close μ={close_returns.mean():.5f}')
        axes[0].axvline(0, color='red', linestyle=':', alpha=0.5, linewidth=1.5)
        axes[0].set_xlabel('Log Returns')
        axes[0].set_ylabel('Density')
        axes[0].set_title('Return Distributions: Open vs Close', fontweight='bold', fontsize=13)
        axes[0].legend(fontsize=9)
        axes[0].grid(True, alpha=0.3)
        
        # Subplot 2: Box plot comparison
        bp = axes[1].boxplot([open_returns, close_returns],
                            labels=['Open', 'Close'],
                            patch_artist=True,
                            boxprops=dict(facecolor='lightblue', alpha=0.7),
                            medianprops=dict(color='red', linewidth=2))
        axes[1].set_ylabel('Log Returns')
        axes[1].set_title('Dispersion Comparison', fontweight='bold', fontsize=13)
        axes[1].grid(True, alpha=0.3, axis='y')
        axes[1].axhline(0, color='red', linestyle=':', alpha=0.5, linewidth=1.5)
        
        # Subplot 3: Cumulative distributions
        open_sorted = np.sort(open_returns)
        close_sorted = np.sort(close_returns)
        axes[2].plot(open_sorted, np.linspace(0, 1, len(open_sorted)),
                    'b-', linewidth=2, label='Open', alpha=0.8)
        axes[2].plot(close_sorted, np.linspace(0, 1, len(close_sorted)),
                    color='orange', linewidth=2, label='Close', alpha=0.8)
        axes[2].axvline(0, color='red', linestyle=':', alpha=0.5, linewidth=1.5)
        axes[2].set_xlabel('Log Returns')
        axes[2].set_ylabel('Cumulative Probability')
        axes[2].set_title('Cumulative Distribution Functions', fontweight='bold', fontsize=13)
        axes[2].legend(fontsize=10)
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = self.figures_path / 'distributions.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved: {output_path}")
        plt.close()
        
        return output_path
    
    def plot_bridge_evolution(self, bridge_results):
        """Plot Schrödinger Bridge evolution"""
        print("\n🌉 Creating bridge evolution plots...")
        
        t_grid = bridge_results['t']
        mu_t = bridge_results['mu']
        sigma_t = bridge_results['sigma']
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Mean evolution
        axes[0].plot(t_grid, mu_t, linewidth=3, color='blue', label='Bridge path μ(t)')
        axes[0].axhline(0, color='red', linestyle='--', alpha=0.7, linewidth=1.5,
                       label='Zero (mean reversion target)')
        axes[0].fill_between(t_grid, mu_t - sigma_t, mu_t + sigma_t,
                            alpha=0.2, color='blue', label='±1σ confidence band')
        axes[0].scatter([0, 1], [mu_t[0], mu_t[-1]], s=150, color='red',
                       zorder=5, edgecolor='black', linewidth=2, label='Observed endpoints')
        axes[0].set_ylabel('Mean Return', fontsize=12, fontweight='bold')
        axes[0].set_title('Schrödinger Bridge: Mean Evolution (Open → Close)',
                         fontsize=14, fontweight='bold')
        axes[0].legend(fontsize=10, loc='best')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xlim([0, 1])
        
        # Add annotations
        axes[0].annotate('Market Open\n(9:30 AM)', xy=(0, mu_t[0]),
                        xytext=(0.15, mu_t[0] * 2 if mu_t[0] != 0 else 0.001),
                        arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                        fontsize=10, ha='center', bbox=dict(boxstyle='round,pad=0.5',
                        facecolor='yellow', alpha=0.3))
        axes[0].annotate('Market Close\n(4:00 PM)', xy=(1, mu_t[-1]),
                        xytext=(0.85, mu_t[-1] * 2 if mu_t[-1] != 0 else -0.001),
                        arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                        fontsize=10, ha='center', bbox=dict(boxstyle='round,pad=0.5',
                        facecolor='lightgreen', alpha=0.3))
        
        # Plot 2: Volatility evolution
        axes[1].plot(t_grid, sigma_t, linewidth=3, color='purple',
                    label='Bridge volatility σ(t)')
        axes[1].scatter([0, 1], [sigma_t[0], sigma_t[-1]], s=150, color='red',
                       zorder=5, edgecolor='black', linewidth=2, label='Observed endpoints')
        axes[1].axhline(sigma_t.mean(), color='green', linestyle='--', alpha=0.5,
                       linewidth=1.5, label=f'Mean volatility: {sigma_t.mean():.5f}')
        axes[1].set_xlabel('Normalized Time (0 = Open, 1 = Close)',
                          fontsize=12, fontweight='bold')
        axes[1].set_ylabel('Volatility', fontsize=12, fontweight='bold')
        axes[1].set_title('Volatility Evolution During Trading Day',
                         fontsize=14, fontweight='bold')
        axes[1].legend(fontsize=10, loc='best')
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xlim([0, 1])
        
        plt.tight_layout()
        output_path = self.figures_path / 'bridge_evolution.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved: {output_path}")
        plt.close()
        
        return output_path
    
    def create_summary_plot(self, open_returns, close_returns, bridge_results):
        """Create comprehensive summary visualization"""
        print("\n📈 Creating summary plot...")
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # Top row: Distributions
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.hist(open_returns, bins=25, density=True, alpha=0.6, color='blue',
                label='Open', edgecolor='black')
        ax1.hist(close_returns, bins=25, density=True, alpha=0.6, color='orange',
                label='Close', edgecolor='black')
        ax1.axvline(0, color='red', linestyle=':', alpha=0.5)
        ax1.set_xlabel('Log Returns')
        ax1.set_ylabel('Density')
        ax1.set_title('Return Distributions', fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Top right: Statistics table
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.axis('off')
        stats_text = f"""
        STATISTICS
        ═══════════════
        Open:
          N = {len(open_returns)}
          μ = {open_returns.mean():.6f}
          σ = {open_returns.std():.6f}
        
        Close:
          N = {len(close_returns)}
          μ = {close_returns.mean():.6f}
          σ = {close_returns.std():.6f}
        
        Bridge:
          Drift = {bridge_results['drift']:.6f}
          Vol = {bridge_results['volatility']:.6f}
          Reversion = {bridge_results['reversion_strength']:.4f}
        """
        ax2.text(0.1, 0.5, stats_text, fontsize=10, fontfamily='monospace',
                verticalalignment='center')
        
        # Middle row: Bridge evolution
        ax3 = fig.add_subplot(gs[1, :])
        t_grid = bridge_results['t']
        mu_t = bridge_results['mu']
        sigma_t = bridge_results['sigma']
        ax3.plot(t_grid, mu_t, linewidth=3, color='blue', label='Mean path')
        ax3.fill_between(t_grid, mu_t - sigma_t, mu_t + sigma_t,
                        alpha=0.2, color='blue', label='±1σ')
        ax3.axhline(0, color='red', linestyle='--', alpha=0.5)
        ax3.set_xlabel('Normalized Time')
        ax3.set_ylabel('Mean Return')
        ax3.set_title('Schrödinger Bridge Evolution', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Bottom row: Volatility + Interpretation
        ax4 = fig.add_subplot(gs[2, :2])
        ax4.plot(t_grid, sigma_t, linewidth=3, color='purple')
        ax4.set_xlabel('Normalized Time')
        ax4.set_ylabel('Volatility')
        ax4.set_title('Volatility Evolution', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        ax5 = fig.add_subplot(gs[2, 2])
        ax5.axis('off')
        interpretation = f"""
        INTERPRETATION
        ═══════════════
        
        ✓ Mean reversion:
          {'YES' if abs(close_returns.mean()) < abs(open_returns.mean()) else 'NO'}
        
        ✓ Volatility change:
          {((close_returns.std() - open_returns.std()) / open_returns.std() * 100):.1f}%
        
        ✓ Bridge reveals:
          {'Negative drift' if bridge_results['drift'] < 0 else 'Positive drift'}
          (toward zero)
        
        ✓ Reversion strength:
          {bridge_results['reversion_strength']:.4f}
          {'(Strong)' if bridge_results['reversion_strength'] > 0.02 else '(Moderate)'}
        """
        ax5.text(0.1, 0.5, interpretation, fontsize=10, fontfamily='monospace',
                verticalalignment='center')
        
        plt.suptitle('Schrödinger Bridge Analysis: Complete Summary',
                    fontsize=16, fontweight='bold', y=0.995)
        
        output_path = self.figures_path / 'summary.png'
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved: {output_path}")
        plt.close()
        
        return output_path


if __name__ == "__main__":
    # Test visualization
    from data_loader import DataLoader
    from bridge_solver import SchrodingerBridge
    
    loader = DataLoader()
    open_ret, close_ret = loader.load_processed_data()
    
    bridge = SchrodingerBridge()
    bridge.fit(open_ret, close_ret)
    bridge_results = bridge.get_bridge_path()
    
    viz = Visualizer()
    viz.plot_distributions(open_ret, close_ret)
    viz.plot_bridge_evolution(bridge_results)
    viz.create_summary_plot(open_ret, close_ret, bridge_results)
    
    print("\n✅ All visualizations created!")

