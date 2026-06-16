"""
Flask Main Application & API Router.
Exposes endpoints for recommendations, detailed stock data, sectors, and histories.
Structured to run as Vercel serverless functions.
"""

import os
import sys
import uuid
import numpy as np

# Ensure root folder is in Python path for local and Vercel module resolution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from api.utils.fetcher import load_local_stocks, fetch_live_stock, fetch_history, update_csv_stock
from api.ai.preprocessor import get_bounds, extract_recommender_features, extract_predictor_features, min_max_scale
from api.ai.recommender import recommend
from api.ai.predictor import generate_synthetic_training_data, get_prediction
from api.database import init_db, save_session, save_recommendation, get_history

app = Flask(__name__)
CORS(app)

# Initialize database on application startup
init_db()

def process_recommendations(recs, all_stocks, X_train, y_train, session_id):
    """Processes recommendations by computing scaling bounds, predicting trends, and saving records."""
    raw_feats = [extract_predictor_features(s, []) for s in all_stocks]
    raw_feats = np.array(raw_feats)
    min_vals = np.min(raw_feats, axis=0)
    max_vals = np.max(raw_feats, axis=0)
    
    results = []
    for rec in recs:
        local_stock = rec['stock']
        ticker = local_stock['ticker']
        
        # Fetch live/real-time data for the chosen recommended stock
        stock = fetch_live_stock(ticker, local_stock)
        
        # Save the live metrics back to stocks.csv in real-time
        update_csv_stock(ticker, stock)
        
        history = fetch_history(ticker, stock['current_price'], stock['volatility'])
        raw_feat = extract_predictor_features(stock, history)
        
        scaled_feat = min_max_scale(raw_feat, min_vals, max_vals)
        trend, confidence = get_prediction(scaled_feat, X_train, y_train)
        
        save_recommendation(session_id, ticker, rec['match_score'], trend)
        results.append({
            'ticker': ticker,
            'company': stock['company'],
            'sector': stock['sector'],
            'current_price': stock['current_price'],
            'match_score': rec['match_score'],
            'prediction': trend,
            'confidence': confidence,
            'market': stock['market']
        })
    return results

def get_ai_explanation(stock, session_id):
    """Generates a personalized explanation of why the stock was recommended."""
    from api.database import get_connection
    profile = None
    if session_id:
        with get_connection() as conn:
            cursor = conn.execute('SELECT * FROM users WHERE session_id = ?', (session_id,))
            row = cursor.fetchone()
            if row:
                profile = dict(row)
                
    ticker = stock['ticker']
    is_id = stock.get('market') == 'ID'
    currency_symbol = "Rp" if is_id else "$"
    price_str = f"{currency_symbol} {stock['current_price']:,.0f}" if is_id else f"{currency_symbol}{stock['current_price']:.2f}"
    market_cap_str = f"Rp {stock['market_cap']:,.0f}" if is_id else f"${stock['market_cap']:,}"
    
    if not profile:
        return f"{ticker} is recommended because of its solid market capitalization of {market_cap_str} and P/E ratio of {stock['pe_ratio']}."
        
    risk_desc = "aligns well with your preference for low-volatility stability" if profile['risk_level'] == 'Low' else "matches your tolerance for high-volatility growth"
    sector_desc = f"directly matches your target sector ({profile['sector']})" if stock['sector'] == profile['sector'] else f"helps diversify your portfolio outside of {profile['sector']}"
    
    return f"{stock['company']} ({ticker}) is recommended for you. It {risk_desc} (volatility: {stock['volatility']:.2f}). Additionally, it {sector_desc} and fits within your budget constraints at a share price of {price_str}."

@app.route('/api/recommend', methods=['POST'])
def handle_recommend():
    """Endpoint to get stock recommendations and their predictions."""
    data = request.get_json() or {}
    session_id = data.get('session_id') or str(uuid.uuid4())
    risk_level = data.get('risk_level', 'Medium')
    budget = float(data.get('budget', 1000.0))
    sector = data.get('sector', 'Technology')
    market = data.get('market', 'US')
    limit = int(data.get('limit', 5))
    
    local_stocks = load_local_stocks()
    market_stocks = [local_stocks[ticker] for ticker in local_stocks if local_stocks[ticker]['market'] == market]
    
    if not market_stocks:
        market_stocks = list(local_stocks.values())
        
    p_bounds = get_bounds(market_stocks, 'current_price')
    v_bounds = get_bounds(market_stocks, 'volatility')
    user_profile = {'risk_level': risk_level, 'budget': budget, 'sector': sector}
    top_recs = recommend(user_profile, market_stocks, p_bounds, v_bounds, limit=limit)
    
    X_train, y_train = generate_synthetic_training_data(200)
    results = process_recommendations(top_recs, market_stocks, X_train, y_train, session_id)
    
    save_session(session_id, risk_level, budget, sector, market)
    return jsonify({'session_id': session_id, 'recommendations': results})

@app.route('/api/stock/<ticker>', methods=['GET'])
def handle_stock_details(ticker):
    """Endpoint returning details and 30-day history for a single ticker."""
    local_stocks = load_local_stocks()
    if ticker not in local_stocks:
        return jsonify({'error': 'Stock not found'}), 404
        
    stock = fetch_live_stock(ticker, local_stocks[ticker])
    history = fetch_history(ticker, stock['current_price'], stock['volatility'])
    
    session_id = request.args.get('session_id')
    explanation = get_ai_explanation(stock, session_id)
    
    return jsonify({
        'stock': stock,
        'history': history,
        'explanation': explanation
    })

@app.route('/api/sectors', methods=['GET'])
def handle_sectors():
    """Endpoint returning all unique stock sectors."""
    local_stocks = load_local_stocks()
    sectors = sorted(list(set(stock['sector'] for stock in local_stocks.values())))
    return jsonify({'sectors': sectors})

@app.route('/api/history/<session_id>', methods=['GET', 'DELETE'])
def handle_history(session_id):
    """Endpoint returning or clearing recommendation history for a session."""
    if request.method == 'DELETE':
        from api.database import clear_history
        clear_history(session_id)
        return jsonify({'success': True, 'message': 'History cleared'})
    return jsonify({'history': get_history(session_id)})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

