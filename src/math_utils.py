import numpy as np
import pandas as pd
from scipy.stats import linregress

def calculate_trend_quality(series):
    """
    Calculates the 'ROC Squared' metric with error handling.
    """
    # 1. Input Validation: Need at least 2 points for a line
    if len(series) < 2:
        return 0.0, 0.0, 0.0
        
    # 2. Handle Data Errors (NaNs or Zeros)
    # Convert to float and drop NaNs just in case
    series = series.astype(float).dropna()
    
    if len(series) < 2:
        return 0.0, 0.0, 0.0

    # 3. Log Calculation (Safe Mode)
    try:
        # np.log will fail on 0 or negative numbers
        if (series <= 0).any():
            return 0.0, 0.0, 0.0
            
        y = np.log(series.values)
        x = np.arange(len(y))
        
        # 4. Linear Regression
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        
        # Check if regression failed (sometimes happens on flat lines)
        if np.isnan(slope) or np.isnan(r_value):
            return 0.0, 0.0, 0.0
        
        # 5. Calculate Score
        r_squared = r_value ** 2
        score = slope * r_squared
        
        return score, slope, r_squared
        
    except Exception as e:
        # Log error in a real app, here we just return 0 to skip the ticker
        return 0.0, 0.0, 0.0
