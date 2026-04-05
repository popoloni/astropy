"""
Plot verification utilities for AstroScope application.
This module provides tools to verify plot outputs against baseline plots.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Tuple, Optional, Dict, Any
import logging
from PIL import Image
import hashlib
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlotVerifier:
    """Class for verifying plot outputs against baseline plots."""
    
    def __init__(self, 
                 baseline_dir: str = "tests/baseline_plots",
                 temp_dir: str = "tests/temp_plots",
                 tolerance: float = 0.01):
        """
        Initialize the PlotVerifier.
        
        Args:
            baseline_dir: Directory containing baseline plots
            temp_dir: Directory for temporary plot storage
            tolerance: Tolerance for numerical comparisons
        """
        self.baseline_dir = baseline_dir
        self.temp_dir = temp_dir
        self.tolerance = tolerance
        
        # Create directories if they don't exist
        os.makedirs(baseline_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
    
    def _get_baseline_name(self, plot_func: callable) -> str:
        """Generate a baseline filename for a plot function."""
        return f"{plot_func.__name__}_baseline.png"
    
    def _get_temp_name(self, plot_func: callable) -> str:
        """Generate a temporary filename for a plot function."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{plot_func.__name__}_{timestamp}.png"
    
    def _load_baseline(self, baseline_name: str) -> Optional[np.ndarray]:
        """Load a baseline plot image."""
        baseline_path = os.path.join(self.baseline_dir, baseline_name)
        if not os.path.exists(baseline_path):
            logger.warning(f"No baseline found at {baseline_path}")
            return None
        return np.array(Image.open(baseline_path))
    
    def _save_plot(self, fig: Figure, filename: str) -> None:
        """Save a plot to a file."""
        fig.savefig(filename, bbox_inches='tight', dpi=100)
    
    def _compare_plots(self, 
                      new_plot: np.ndarray, 
                      baseline_plot: np.ndarray) -> Dict[str, Any]:
        """
        Compare two plot images.
        
        Returns:
            Dictionary containing comparison results
        """
        if new_plot.shape != baseline_plot.shape:
            return {
                'match': False,
                'error': 'Shape mismatch',
                'new_shape': new_plot.shape,
                'baseline_shape': baseline_plot.shape
            }
        
        # Calculate mean absolute difference
        diff = np.abs(new_plot.astype(float) - baseline_plot.astype(float))
        mean_diff = np.mean(diff)
        
        # Calculate color distribution differences
        new_colors = np.mean(new_plot, axis=(0, 1))
        baseline_colors = np.mean(baseline_plot, axis=(0, 1))
        color_diff = np.abs(new_colors - baseline_colors)
        
        return {
            'match': mean_diff <= self.tolerance,
            'mean_difference': float(mean_diff),
            'color_differences': color_diff.tolist(),
            'tolerance': self.tolerance
        }
    
    def verify_plot(self, 
                   plot_func: callable, 
                   *args, 
                   **kwargs) -> Dict[str, Any]:
        """
        Verify a plot function against its baseline.
        
        Args:
            plot_func: Function that generates a plot
            *args: Arguments for plot_func
            **kwargs: Keyword arguments for plot_func
            
        Returns:
            Dictionary containing verification results
        """
        # Generate new plot
        fig = plot_func(*args, **kwargs)
        temp_path = os.path.join(self.temp_dir, self._get_temp_name(plot_func))
        self._save_plot(fig, temp_path)
        new_plot = np.array(Image.open(temp_path))
        
        # Get baseline plot
        baseline_name = self._get_baseline_name(plot_func)
        baseline_plot = self._load_baseline(baseline_name)
        
        if baseline_plot is None:
            # Create new baseline
            baseline_path = os.path.join(self.baseline_dir, baseline_name)
            self._save_plot(fig, baseline_path)
            plt.close(fig)
            return {
                'match': True,
                'message': 'Created new baseline',
                'baseline_path': baseline_path
            }
        
        # Compare plots
        result = self._compare_plots(new_plot, baseline_plot)
        
        # Clean up temporary file and figure
        os.remove(temp_path)
        plt.close(fig)
        
        return result
    
    def verify_metadata(self, 
                       plot_func: callable, 
                       metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify plot metadata against baseline metadata.
        
        Args:
            plot_func: Function that generates a plot
            metadata: Dictionary of metadata to verify
            
        Returns:
            Dictionary containing verification results
        """
        baseline_name = f"{plot_func.__name__}_metadata.json"
        baseline_path = os.path.join(self.baseline_dir, baseline_name)
        
        if not os.path.exists(baseline_path):
            # Create new baseline
            with open(baseline_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            return {
                'match': True,
                'message': 'Created new metadata baseline',
                'baseline_path': baseline_path
            }
        
        # Load and compare metadata
        with open(baseline_path, 'r') as f:
            baseline_metadata = json.load(f)
        
        # Compare metadata
        differences = {}
        for key in set(metadata.keys()) | set(baseline_metadata.keys()):
            if key not in metadata:
                differences[key] = {'type': 'missing_in_new', 'value': None}
            elif key not in baseline_metadata:
                differences[key] = {'type': 'new_key', 'value': metadata[key]}
            elif metadata[key] != baseline_metadata[key]:
                differences[key] = {
                    'type': 'different',
                    'new_value': metadata[key],
                    'baseline_value': baseline_metadata[key]
                }
        
        return {
            'match': len(differences) == 0,
            'differences': differences
        }
