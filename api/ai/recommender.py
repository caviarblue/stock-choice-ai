"""
Stock Recommender AI.
Implements content-based filtering using Cosine Similarity built from scratch
with NumPy. Ranks stocks against a user preference profile.
"""

import numpy as np
from api.ai.preprocessor import min_max_scale, encode_sector, extract_recommender_features

def cosine_similarity(vector_a, vector_b):
    """
    Computes the cosine similarity between two vectors.
    
    Formula:
        cosine_sim = dot(A, B) / (norm(A) * norm(B))
    
    Math Explanation:
        - dot(A, B): Measures the alignment of directions between vectors A and B.
          Calculated as: sum(A_i * B_i)
        - norm(A) * norm(B): Normalizes the result by the product of their Euclidean lengths.
          Calculated as: sqrt(sum(A_i^2)) * sqrt(sum(B_i^2))
        - If either norm is zero, we return 0.0 to prevent division by zero.
    """
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))

def build_user_vector(risk_level, budget, sector, price_bounds, vol_bounds):
    """
    Encodes the user preferences into a normalized 7-dimensional profile vector.
    
    Dimensions:
        - 1: Normalized risk level (Low=0.1, Medium=0.5, High=0.9)
        - 2: Normalized budget (clamped to price bounds of current dataset)
        - 3-7: One-hot encoded sector preference vector
    """
    risk_map = {'Low': 0.1, 'Medium': 0.5, 'High': 0.9}
    risk_score = risk_map.get(risk_level, 0.5)
    
    # Scale budget relative to the current stock prices
    norm_budget = min_max_scale(budget, price_bounds[0], price_bounds[1])
    # Clamp to [0, 1] range to avoid out-of-bounds vectors
    norm_budget = max(0.0, min(1.0, float(norm_budget)))
    
    sector_vec = encode_sector(sector)
    return np.hstack(([risk_score, norm_budget], sector_vec))

def recommend(user_profile, stocks, price_bounds, vol_bounds, limit=5):
    """
    Compares user profile vector against all stock vectors using cosine similarity.
    Enforces a hard budget constraint: IDX stocks (market == 'ID') require purchasing
    a minimum of 1 lot (100 shares), while US stocks require a minimum of 1 share.
    
    Returns:
        Top ranked stocks (up to limit) with match scores (percentage values, 0-100%).
    """
    user_vector = build_user_vector(
        user_profile['risk_level'],
        user_profile['budget'],
        user_profile['sector'],
        price_bounds,
        vol_bounds
    )
    
    recommendations = []
    for stock in stocks:
        # Enforce minimum trade unit constraint: 100 shares for IDX, 1 share for US
        is_id = stock.get('market') == 'ID'
        min_unit = 100 if is_id else 1
        min_cost = stock['current_price'] * min_unit
        
        # Hard filter: Exclude stocks that the user cannot afford at least 1 unit of
        if min_cost > user_profile['budget']:
            continue
            
        stock_vector = extract_recommender_features(stock, price_bounds, vol_bounds)
        similarity = cosine_similarity(user_vector, stock_vector)
        
        # Convert similarity (-1 to 1 range, but here 0 to 1 because all components >= 0) to percentage
        match_score = max(0.0, min(100.0, float(similarity) * 100.0))
        
        recommendations.append({
            'stock': stock,
            'match_score': round(match_score, 2)
        })
        
    # Sort descending by match score
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)
    return recommendations[:limit]
