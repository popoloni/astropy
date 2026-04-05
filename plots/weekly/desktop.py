"""
Desktop weekly analysis plotting module for AstroScope.

This module provides comprehensive weekly analysis plotting functionality optimized
for desktop platforms, including detailed statistical visualizations, multi-panel
analysis charts, and comprehensive weekly comparison plots.

Features:
- Comprehensive 6-panel weekly analysis plots
- Statistical analysis and comparison charts
- Moon phase and illumination tracking
- Mosaic opportunity analysis
- Object distribution visualization
- High-resolution plotting for detailed analysis
"""

import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from config.settings import *

# Desktop-specific constants
DESKTOP_FIGURE_SIZE = (18, 12)
DESKTOP_DPI = 100
DESKTOP_FONT_SIZE = 12
DESKTOP_TITLE_SIZE = 16
DESKTOP_LABEL_SIZE = 10

def plot_weekly_analysis(weekly_results, period_desc="analysis period"):
    """
    Create comprehensive plots for weekly analysis.
    
    This function creates a 6-panel visualization showing:
    1. Observable objects by week (scatter plot with scores)
    2. Moon-free objects by week (bar chart)
    3. Mosaic opportunities by week (bar chart)
    4. Weekly astrophotography scores (bar chart with best week highlighted)
    5. Moon phase throughout weeks (line plot)
    6. Object distribution with config compliance (grouped bar chart)
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: The complete weekly analysis figure
    """
    weeks = sorted(weekly_results.keys())
    
    if not weeks:
        # Create empty plot for no data
        fig, ax = plt.subplots(figsize=DESKTOP_FIGURE_SIZE)
        ax.text(0.5, 0.5, 'No weekly data available', 
                ha='center', va='center', fontsize=DESKTOP_FONT_SIZE,
                transform=ax.transAxes)
        ax.set_title(f'Weekly Analysis - {period_desc.title()}', 
                    fontsize=DESKTOP_TITLE_SIZE)
        return fig
    
    # Extract data for plotting
    observable_objects = [weekly_results[w]['observable_objects'] for w in weeks]
    config_compliant = [weekly_results[w]['sufficient_time_objects'] for w in weeks]
    moon_illuminations = [weekly_results[w]['moon_illumination'] * 100 for w in weeks]
    moon_free_counts = [len(weekly_results[w]['moon_free_objects']) for w in weeks]
    mosaic_counts = [len(weekly_results[w]['mosaic_groups']) for w in weeks]
    scores = [weekly_results[w]['score'] for w in weeks]
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=DESKTOP_FIGURE_SIZE, dpi=DESKTOP_DPI)
    fig.suptitle(f'Weekly Astrophotography Analysis - {period_desc.title()}', 
                fontsize=DESKTOP_TITLE_SIZE, fontweight='bold')
    
    # Plot 1: Observable objects by week
    ax1 = axes[0, 0]
    scatter = ax1.scatter(weeks, observable_objects, c=scores, cmap='viridis', 
                         s=100, alpha=0.7, edgecolors='black', linewidth=0.5)
    ax1.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax1.set_ylabel('Observable Objects', fontsize=DESKTOP_LABEL_SIZE)
    ax1.set_title('Observable Objects by Week', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    cbar1 = plt.colorbar(scatter, ax=ax1, label='Week Score')
    cbar1.ax.tick_params(labelsize=DESKTOP_LABEL_SIZE-1)
    
    # Plot 2: Moon-free objects by week
    ax2 = axes[0, 1]
    bars2 = ax2.bar(weeks, moon_free_counts, alpha=0.7, color='green', 
                   edgecolor='darkgreen', linewidth=0.5)
    ax2.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_ylabel('Moon-Free Objects', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_title('Moon-Free Objects by Week', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, count in zip(bars2, moon_free_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                f'{count}', ha='center', va='bottom', fontsize=DESKTOP_LABEL_SIZE-1)
    
    # Plot 3: Mosaic opportunities
    ax3 = axes[0, 2]
    bars3 = ax3.bar(weeks, mosaic_counts, alpha=0.7, color='orange',
                   edgecolor='darkorange', linewidth=0.5)
    ax3.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax3.set_ylabel('Mosaic Groups', fontsize=DESKTOP_LABEL_SIZE)
    ax3.set_title('Mosaic Opportunities by Week', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, count in zip(bars3, mosaic_counts):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{count}', ha='center', va='bottom', fontsize=DESKTOP_LABEL_SIZE-1)
    
    # Plot 4: Week scores
    ax4 = axes[1, 0]
    score_bars = ax4.bar(weeks, scores, alpha=0.7, color='purple',
                        edgecolor='darkviolet', linewidth=0.5)
    ax4.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax4.set_ylabel('Astrophotography Score', fontsize=DESKTOP_LABEL_SIZE)
    ax4.set_title('Weekly Astrophotography Scores', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # Highlight best week
    if weeks:
        best_week = max(weeks, key=lambda w: weekly_results[w]['score'])
        best_week_idx = weeks.index(best_week)
        score_bars[best_week_idx].set_color('gold')
        score_bars[best_week_idx].set_edgecolor('darkgoldenrod')
        
        # Add annotation for best week
        best_score = scores[best_week_idx]
        ax4.annotate(f'Best Week\n{best_score:.1f}', 
                    xy=(best_week, best_score), 
                    xytext=(best_week, best_score + max(scores) * 0.1),
                    ha='center', va='bottom',
                    fontsize=DESKTOP_LABEL_SIZE-1, fontweight='bold',
                    arrowprops=dict(arrowstyle='->', color='darkgoldenrod', lw=1.5))
    
    # Plot 5: Moon phase throughout weeks
    ax5 = axes[1, 1]
    moon_phases = [weekly_results[w]['moon_phase'] * 100 for w in weeks]
    line = ax5.plot(weeks, moon_phases, 'o-', color='blue', linewidth=2, 
                   markersize=8, markerfacecolor='lightblue', 
                   markeredgecolor='darkblue', markeredgewidth=1)
    ax5.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax5.set_ylabel('Moon Phase (%)', fontsize=DESKTOP_LABEL_SIZE)
    ax5.set_title('Moon Phase by Week', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax5.grid(True, alpha=0.3)
    ax5.axhline(y=50, color='red', linestyle='--', alpha=0.7, linewidth=2, label='Full Moon')
    ax5.axhline(y=0, color='black', linestyle='--', alpha=0.7, linewidth=2, label='New Moon')
    ax5.legend(fontsize=DESKTOP_LABEL_SIZE-1)
    ax5.set_ylim(-5, 105)
    
    # Plot 6: Objects distribution with config compliance
    ax6 = axes[1, 2]
    moon_affected_counts = [len(weekly_results[w]['moon_affected_objects']) for w in weeks]
    
    width = 0.25
    x = np.arange(len(weeks))
    bars6a = ax6.bar(x - width, config_compliant, width, label='Config-Compliant', 
                    alpha=0.7, color='blue', edgecolor='darkblue', linewidth=0.5)
    bars6b = ax6.bar(x, moon_free_counts, width, label='Moon-Free', 
                    alpha=0.7, color='green', edgecolor='darkgreen', linewidth=0.5)
    bars6c = ax6.bar(x + width, moon_affected_counts, width, label='Moon-Affected', 
                    alpha=0.7, color='red', edgecolor='darkred', linewidth=0.5)
    
    ax6.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax6.set_ylabel('Object Count', fontsize=DESKTOP_LABEL_SIZE)
    ax6.set_title('Object Distribution by Week', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax6.set_xticks(x)
    ax6.set_xticklabels([str(w) for w in weeks])
    ax6.legend(fontsize=DESKTOP_LABEL_SIZE-1)
    ax6.grid(True, alpha=0.3)
    
    # Adjust layout and spacing
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Make room for suptitle
    
    return fig

def create_weekly_comparison_plot(weekly_results, period_desc="analysis period"):
    """
    Create a detailed comparison plot showing weekly trends.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: The weekly comparison figure
    """
    weeks = sorted(weekly_results.keys())
    
    if not weeks:
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.5, 'No weekly data available for comparison', 
                ha='center', va='center', fontsize=DESKTOP_FONT_SIZE,
                transform=ax.transAxes)
        return fig
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), dpi=DESKTOP_DPI)
    fig.suptitle(f'Weekly Trends Comparison - {period_desc.title()}', 
                fontsize=DESKTOP_TITLE_SIZE, fontweight='bold')
    
    # Extract data
    observable_objects = [weekly_results[w]['observable_objects'] for w in weeks]
    config_compliant = [weekly_results[w]['sufficient_time_objects'] for w in weeks]
    moon_free_counts = [len(weekly_results[w]['moon_free_objects']) for w in weeks]
    scores = [weekly_results[w]['score'] for w in weeks]
    moon_illuminations = [weekly_results[w]['moon_illumination'] * 100 for w in weeks]
    
    # Top plot: Object counts and scores
    ax1_twin = ax1.twinx()
    
    line1 = ax1.plot(weeks, observable_objects, 'o-', color='blue', linewidth=2, 
                    markersize=6, label='Observable Objects')
    line2 = ax1.plot(weeks, config_compliant, 's-', color='green', linewidth=2, 
                    markersize=6, label='Config-Compliant')
    line3 = ax1.plot(weeks, moon_free_counts, '^-', color='orange', linewidth=2, 
                    markersize=6, label='Moon-Free')
    
    line4 = ax1_twin.plot(weeks, scores, 'D-', color='red', linewidth=2, 
                         markersize=6, label='Week Score')
    
    ax1.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax1.set_ylabel('Object Count', fontsize=DESKTOP_LABEL_SIZE, color='black')
    ax1_twin.set_ylabel('Week Score', fontsize=DESKTOP_LABEL_SIZE, color='red')
    ax1.set_title('Object Counts and Weekly Scores', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Combine legends
    lines1 = line1 + line2 + line3
    lines2 = line4
    labels1 = [l.get_label() for l in lines1]
    labels2 = [l.get_label() for l in lines2]
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=DESKTOP_LABEL_SIZE-1)
    
    # Bottom plot: Moon illumination
    ax2.fill_between(weeks, moon_illuminations, alpha=0.3, color='lightblue', label='Moon Illumination')
    ax2.plot(weeks, moon_illuminations, 'o-', color='darkblue', linewidth=2, markersize=6)
    ax2.set_xlabel('Week Number', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_ylabel('Moon Illumination (%)', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_title('Moon Illumination Throughout Period', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(0, 100)
    
    # Add reference lines
    ax2.axhline(y=25, color='green', linestyle='--', alpha=0.7, label='Good (< 25%)')
    ax2.axhline(y=75, color='red', linestyle='--', alpha=0.7, label='Poor (> 75%)')
    ax2.legend(fontsize=DESKTOP_LABEL_SIZE-1)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    return fig

def create_weekly_statistics_plot(weekly_results, period_desc="analysis period"):
    """
    Create a statistical summary plot for weekly analysis.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: The weekly statistics figure
    """
    weeks = sorted(weekly_results.keys())
    
    if not weeks:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, 'No weekly data available for statistics', 
                ha='center', va='center', fontsize=DESKTOP_FONT_SIZE,
                transform=ax.transAxes)
        return fig
    
    # Calculate statistics
    scores = [weekly_results[w]['score'] for w in weeks]
    observable_objects = [weekly_results[w]['observable_objects'] for w in weeks]
    config_compliant = [weekly_results[w]['sufficient_time_objects'] for w in weeks]
    moon_free_counts = [len(weekly_results[w]['moon_free_objects']) for w in weeks]
    
    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10), dpi=DESKTOP_DPI)
    fig.suptitle(f'Weekly Analysis Statistics - {period_desc.title()}', 
                fontsize=DESKTOP_TITLE_SIZE, fontweight='bold')
    
    # Plot 1: Score distribution
    ax1.hist(scores, bins=min(10, len(weeks)), alpha=0.7, color='purple', 
            edgecolor='darkviolet', linewidth=1)
    ax1.axvline(np.mean(scores), color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {np.mean(scores):.1f}')
    ax1.axvline(np.median(scores), color='orange', linestyle='--', linewidth=2, 
               label=f'Median: {np.median(scores):.1f}')
    ax1.set_xlabel('Week Score', fontsize=DESKTOP_LABEL_SIZE)
    ax1.set_ylabel('Frequency', fontsize=DESKTOP_LABEL_SIZE)
    ax1.set_title('Score Distribution', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax1.legend(fontsize=DESKTOP_LABEL_SIZE-1)
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Observable objects distribution
    ax2.hist(observable_objects, bins=min(10, len(weeks)), alpha=0.7, color='blue',
            edgecolor='darkblue', linewidth=1)
    ax2.axvline(np.mean(observable_objects), color='red', linestyle='--', linewidth=2,
               label=f'Mean: {np.mean(observable_objects):.1f}')
    ax2.set_xlabel('Observable Objects', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_ylabel('Frequency', fontsize=DESKTOP_LABEL_SIZE)
    ax2.set_title('Observable Objects Distribution', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax2.legend(fontsize=DESKTOP_LABEL_SIZE-1)
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Box plot comparison
    data_to_plot = [scores, observable_objects, config_compliant, moon_free_counts]
    labels = ['Scores', 'Observable', 'Config-Compliant', 'Moon-Free']
    
    # Normalize data for comparison
    normalized_data = []
    for data in data_to_plot:
        if max(data) > 0:
            normalized_data.append([x / max(data) * 100 for x in data])
        else:
            normalized_data.append(data)
    
    box_plot = ax3.boxplot(normalized_data, tick_labels=labels, patch_artist=True)
    colors = ['purple', 'blue', 'green', 'orange']
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_ylabel('Normalized Values (%)', fontsize=DESKTOP_LABEL_SIZE)
    ax3.set_title('Data Distribution Comparison', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Correlation matrix
    import matplotlib.patches as patches
    
    # Calculate correlations
    data_matrix = np.array([scores, observable_objects, config_compliant, moon_free_counts])
    corr_matrix = np.corrcoef(data_matrix)
    
    im = ax4.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
    ax4.set_xticks(range(len(labels)))
    ax4.set_yticks(range(len(labels)))
    ax4.set_xticklabels(labels, rotation=45, ha='right')
    ax4.set_yticklabels(labels)
    ax4.set_title('Correlation Matrix', fontsize=DESKTOP_FONT_SIZE, fontweight='bold')
    
    # Add correlation values
    for i in range(len(labels)):
        for j in range(len(labels)):
            text = ax4.text(j, i, f'{corr_matrix[i, j]:.2f}',
                           ha="center", va="center", color="black", fontweight='bold')
    
    plt.colorbar(im, ax=ax4, label='Correlation Coefficient')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    return fig

def create_weekly_summary_table_plot(weekly_results, period_desc="analysis period"):
    """
    Create a table-style plot summarizing weekly results.
    
    Args:
        weekly_results (dict): Dictionary containing weekly analysis results
        period_desc (str): Description of the analysis period
        
    Returns:
        matplotlib.figure.Figure: The weekly summary table figure
    """
    weeks = sorted(weekly_results.keys())
    
    if not weeks:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(0.5, 0.5, 'No weekly data available for summary table', 
                ha='center', va='center', fontsize=DESKTOP_FONT_SIZE,
                transform=ax.transAxes)
        return fig
    
    # Prepare data for table
    table_data = []
    headers = ['Week', 'Score', 'Observable', 'Config', 'Moon-Free', 'Mosaics', 'Moon %']
    
    for week in weeks:
        data = weekly_results[week]
        row = [
            str(week),
            f"{data['score']:.1f}",
            str(data['observable_objects']),
            str(data['sufficient_time_objects']),
            str(len(data['moon_free_objects'])),
            str(len(data['mosaic_groups'])),
            f"{data['moon_illumination']*100:.1f}%"
        ]
        table_data.append(row)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, max(6, len(weeks) * 0.4 + 2)), dpi=DESKTOP_DPI)
    ax.axis('tight')
    ax.axis('off')
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers, 
                    cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(DESKTOP_LABEL_SIZE)
    table.scale(1.2, 1.5)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Highlight best week
    if weeks:
        best_week = max(weeks, key=lambda w: weekly_results[w]['score'])
        best_week_idx = weeks.index(best_week) + 1  # +1 for header row
        for j in range(len(headers)):
            table[(best_week_idx, j)].set_facecolor('#FFD700')
            table[(best_week_idx, j)].set_text_props(weight='bold')
    
    # Color code cells based on values
    for i, week in enumerate(weeks):
        row_idx = i + 1  # +1 for header row
        data = weekly_results[week]
        
        # Color score cell
        score = data['score']
        if score >= 80:
            color = '#90EE90'  # Light green
        elif score >= 60:
            color = '#FFFFE0'  # Light yellow
        else:
            color = '#FFB6C1'  # Light pink
        table[(row_idx, 1)].set_facecolor(color)
        
        # Color moon illumination cell
        moon_pct = data['moon_illumination'] * 100
        if moon_pct <= 25:
            color = '#90EE90'  # Light green
        elif moon_pct <= 75:
            color = '#FFFFE0'  # Light yellow
        else:
            color = '#FFB6C1'  # Light pink
        table[(row_idx, 6)].set_facecolor(color)
    
    plt.title(f'Weekly Analysis Summary Table - {period_desc.title()}', 
             fontsize=DESKTOP_TITLE_SIZE, fontweight='bold', pad=20)
    
    return fig 