"""
AI Algorithm Validation Suite.
Tests custom implementations of min-max scaling, sector encoding,
cosine similarity, and logistic regression from scratch.
"""

import sys
import os
import numpy as np

# Add parent dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.ai.preprocessor import min_max_scale, encode_sector
from api.ai.recommender import cosine_similarity, build_user_vector
from api.ai.predictor import LogisticRegression, generate_synthetic_training_data

def test_min_max_scale():
    print("Testing Min-Max scaling...")
    values = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
    scaled = min_max_scale(values, 10.0, 50.0)
    expected = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    assert np.allclose(scaled, expected), f"Expected {expected}, got {scaled}"
    
    # Test single float
    assert min_max_scale(30.0, 10.0, 50.0) == 0.5
    print("✓ Min-Max scaling works.")

def test_sector_encoding():
    print("Testing Sector One-Hot encoding...")
    from api.ai.preprocessor import SECTORS
    for index, sector in enumerate(SECTORS):
        vec = encode_sector(sector)
        expected = np.zeros(len(SECTORS))
        expected[index] = 1.0
        assert np.array_equal(vec, expected), f"Failed for {sector}"
    print("✓ Sector encoding works.")

def test_cosine_similarity():
    print("Testing Cosine Similarity...")
    a = np.array([1.0, 0.0, 1.0])
    b = np.array([1.0, 0.0, 1.0])
    assert np.isclose(cosine_similarity(a, b), 1.0), "Identical vectors should have similarity 1.0"
    
    c = np.array([0.0, 1.0, 0.0])
    assert np.isclose(cosine_similarity(a, c), 0.0), "Orthogonal vectors should have similarity 0.0"
    
    # Test random math alignment
    v1 = np.array([3.0, 4.0])  # norm = 5
    v2 = np.array([4.0, 3.0])  # norm = 5, dot = 24
    expected = 24.0 / 25.0 # 0.96
    assert np.isclose(cosine_similarity(v1, v2), expected), f"Expected {expected}, got {cosine_similarity(v1, v2)}"
    print("✓ Cosine Similarity works.")

def test_logistic_regression():
    print("Testing Logistic Regression predictor...")
    # Initialize
    lr = LogisticRegression(learning_rate=0.1, iterations=100)
    
    # Sigmoid test
    assert np.isclose(lr.sigmoid(0.0), 0.5), "Sigmoid(0) should be 0.5"
    assert lr.sigmoid(100.0) > 0.99, "Sigmoid(100) should be close to 1.0"
    assert lr.sigmoid(-100.0) < 0.01, "Sigmoid(-100) should be close to 0.0"
    
    # Fit test on toy synthetic data
    X, y = generate_synthetic_training_data(100)
    lr.fit(X, y)
    
    preds = lr.predict_probability(X)
    loss = lr.compute_loss(y, preds)
    print(f"  Training loss: {loss:.4f}")
    assert loss < 1.0, "Loss should converge to a low value"
    
    # Predict trend test
    features = X[0]
    trend, conf = lr.predict_trend(features)
    assert trend in ["Up", "Down", "Neutral"], f"Invalid trend returned: {trend}"
    assert 0.0 <= conf <= 100.0, f"Invalid confidence: {conf}%"
    print(f"  Sample prediction: {trend} with {conf:.2f}% confidence (true label: {y[0]})")
    print("✓ Logistic Regression works.")

def test_recommend_budget_constraint():
    print("Testing Recommender budget constraints...")
    from api.ai.recommender import recommend
    
    # Mock stock list
    # MLPT.JK: price = 20000, market = ID. 1 lot = 20000 * 100 = 2000000.
    # Cheap.JK: price = 1000, market = ID. 1 lot = 1000 * 100 = 100000.
    # USStock: price = 150, market = US. 1 share = 150.
    stocks = [
        {
            'ticker': 'MLPT.JK',
            'company': 'Multipolar Technology',
            'sector': 'Technology',
            'current_price': 20000.0,
            'market_cap': 1e12,
            'pe_ratio': 15.0,
            'volatility': 0.25,
            'week_52_high': 25000.0,
            'week_52_low': 15000.0,
            'avg_volume': 1e6,
            'market': 'ID'
        },
        {
            'ticker': 'CHEAP.JK',
            'company': 'Cheap Stock',
            'sector': 'Technology',
            'current_price': 1000.0,
            'market_cap': 1e11,
            'pe_ratio': 10.0,
            'volatility': 0.20,
            'week_52_high': 1200.0,
            'week_52_low': 800.0,
            'avg_volume': 1e5,
            'market': 'ID'
        },
        {
            'ticker': 'USSTOCK',
            'company': 'US Stock',
            'sector': 'Technology',
            'current_price': 150.0,
            'market_cap': 1e10,
            'pe_ratio': 20.0,
            'volatility': 0.30,
            'week_52_high': 200.0,
            'week_52_low': 100.0,
            'avg_volume': 1e5,
            'market': 'US'
        }
    ]
    
    # 1. Budget = 1,000,000 IDR (1M IDR)
    # MLPT lot cost is 2,000,000 IDR -> should be filtered out.
    # CHEAP lot cost is 100,000 IDR -> should be kept.
    profile = {
        'risk_level': 'Medium',
        'budget': 1000000.0,
        'sector': 'Technology'
    }
    
    recs = recommend(profile, stocks, price_bounds=(800.0, 25000.0), vol_bounds=(0.20, 0.30), limit=5)
    tickers = [r['stock']['ticker'] for r in recs]
    
    assert 'MLPT.JK' not in tickers, "MLPT.JK is too expensive for 1M IDR budget (1 lot = 2M IDR)"
    assert 'CHEAP.JK' in tickers, "CHEAP.JK should be recommended"
    
    # 2. Budget = 3,000,000 IDR (3M IDR)
    # MLPT lot cost is 2,000,000 IDR -> should be kept.
    profile_rich = {
        'risk_level': 'Medium',
        'budget': 3000000.0,
        'sector': 'Technology'
    }
    recs_rich = recommend(profile_rich, stocks, price_bounds=(800.0, 25000.0), vol_bounds=(0.20, 0.30), limit=5)
    tickers_rich = [r['stock']['ticker'] for r in recs_rich]
    assert 'MLPT.JK' in tickers_rich, "MLPT.JK should be recommended with 3M IDR budget"
    
    print("✓ Recommender budget constraints work.")

if __name__ == "__main__":
    print("=== STARTING AI VALIDATION ===")
    test_min_max_scale()
    test_sector_encoding()
    test_cosine_similarity()
    test_logistic_regression()
    test_recommend_budget_constraint()
    print("=== ALL TESTS PASSED SUCCESSFULLY ===")
