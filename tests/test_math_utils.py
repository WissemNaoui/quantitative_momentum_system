"""
Quick test to verify the math_utils module works correctly.
"""

import sys
sys.path.insert(0, '/home/wissem/.gemini/antigravity/scratch/quantitative_momentum_system/src')

import numpy as np
import pandas as pd
from math_utils import calculate_trend_quality


def test_uptrend():
    """Test with a perfect uptrend."""
    # Perfect exponential growth
    prices = pd.Series([100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 120])
    score, slope, r2 = calculate_trend_quality(prices)
    
    print("Test 1: Perfect Uptrend")
    print(f"  Score: {score:.6f}")
    print(f"  Slope: {slope:.6f}")
    print(f"  R²: {r2:.6f}")
    
    assert slope > 0, "Slope should be positive for uptrend"
    assert r2 > 0.95, "R² should be high for smooth trend"
    assert score > 0, "Score should be positive"
    print("  ✅ PASS\n")


def test_downtrend():
    """Test with a downtrend."""
    prices = pd.Series([120, 118, 116, 114, 112, 110, 108, 106, 104, 102, 100])
    score, slope, r2 = calculate_trend_quality(prices)
    
    print("Test 2: Downtrend")
    print(f"  Score: {score:.6f}")
    print(f"  Slope: {slope:.6f}")
    print(f"  R²: {r2:.6f}")
    
    assert slope < 0, "Slope should be negative for downtrend"
    assert score < 0, "Score should be negative"
    print("  ✅ PASS\n")


def test_noisy_trend():
    """Test with a noisy uptrend."""
    # Uptrend with noise
    prices = pd.Series([100, 103, 101, 106, 104, 109, 107, 112, 110, 115, 113])
    score, slope, r2 = calculate_trend_quality(prices)
    
    print("Test 3: Noisy Uptrend")
    print(f"  Score: {score:.6f}")
    print(f"  Slope: {slope:.6f}")
    print(f"  R²: {r2:.6f}")
    
    assert slope > 0, "Slope should still be positive"
    assert r2 < 0.95, "R² should be lower due to noise"
    assert score > 0, "Score should still be positive but lower"
    print("  ✅ PASS\n")


def test_flat():
    """Test with flat prices."""
    prices = pd.Series([100] * 20)
    score, slope, r2 = calculate_trend_quality(prices)
    
    print("Test 4: Flat (No Trend)")
    print(f"  Score: {score:.6f}")
    print(f"  Slope: {slope:.6f}")
    print(f"  R²: {r2:.6f}")
    
    assert abs(slope) < 0.001, "Slope should be near zero"
    assert abs(score) < 0.001, "Score should be near zero"
    print("  ✅ PASS\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing math_utils.calculate_trend_quality()")
    print("=" * 60 + "\n")
    
    test_uptrend()
    test_downtrend()
    test_noisy_trend()
    test_flat()
    
    print("=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
