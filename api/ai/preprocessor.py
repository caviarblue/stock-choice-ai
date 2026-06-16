"""
Stock Preprocessor.
Performs data cleaning, min-max scaling, and categorical encoding
of stock and user features using pure Python and NumPy.
"""

import numpy as np

SECTORS = ['Technology', 'Energy', 'Healthcare', 'Financials', 'Consumer']

def encode_sector(sector):
    """One-hot encodes a sector name into a 5-element NumPy array."""
    vector = np.zeros(len(SECTORS))
    if sector in SECTORS:
        index = SECTORS.index(sector)
        vector[index] = 1.0
    return vector

def min_max_scale(values, min_val, max_val):
    """Scales a NumPy array or float to 0-1 range using min-max normalization."""
    denominator = max_val - min_val
    if np.ndim(denominator) > 0:
        num = values - min_val
        result = np.zeros_like(num, dtype=float)
        non_zero = (denominator != 0)
        result[non_zero] = num[non_zero] / denominator[non_zero]
        return result
    else:
        if denominator == 0:
            return np.zeros_like(values) if isinstance(values, np.ndarray) else 0.0
        return (values - min_val) / denominator

def get_bounds(stocks, key):
    """Extracts the minimum and maximum values of a key from a list of stocks."""
    values = [stock[key] for stock in stocks]
    return float(min(values)), float(max(values))

def extract_recommender_features(stock, price_bounds, vol_bounds):
    """Extracts and scales features for the content-based recommender."""
    norm_price = min_max_scale(stock['current_price'], price_bounds[0], price_bounds[1])
    norm_vol = min_max_scale(stock['volatility'], vol_bounds[0], vol_bounds[1])
    sector_vec = encode_sector(stock['sector'])
    return np.hstack(([norm_vol, norm_price], sector_vec))

def extract_predictor_features(stock, history):
    """Extracts raw features for the trend predictor from stock data and history."""
    vol = stock['volatility']
    pe = stock['pe_ratio']
    current_price = stock['current_price']
    
    # Calculate recent price change from 30-day history
    if history and len(history) > 1:
        start_price = history[0]['price']
        price_change = (current_price - start_price) / start_price
    else:
        price_change = 0.05
        
    vol_trend = 1.0  # Fallback volume trend ratio
    dist_52w_high = (stock['week_52_high'] - current_price) / stock['week_52_high']
    
    return np.array([vol, pe, price_change, vol_trend, dist_52w_high])
