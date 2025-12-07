import numpy as np
from scipy.stats import linregress

def calculate_trend_quality(series):
    """
    Calculates the 'ROC Squared' metric.
    
    This metric combines momentum (slope) with consistency (R²) to identify
    stocks that are moving up in a smooth, predictable manner.
    
    Args:
        series: A pandas Series of prices (e.g., last 20 days)
    
    Returns:
        tuple: (score, slope, r_squared)
            - score: The combined metric (slope * R²)
            - slope: The log-linear trend slope (momentum)
            - r_squared: Coefficient of determination (smoothness)
    
    Theory:
        - Using log prices converts exponential growth to linear growth
        - Slope measures the rate of price increase
        - R² measures how well prices fit a straight line (low noise)
        - High score = Strong uptrend with low volatility
    """
    # Use Log prices to handle percentage growth linearly
    y = np.log(series.values)
    x = np.arange(len(y))
    
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    
    # Metric: Slope (Momentum) * R^2 (Smoothness)
    # We want stocks moving UP smoothly.
    r_squared = r_value ** 2
    score = slope * r_squared
    
    return score, slope, r_squared
