"""
Stock Data Fetcher Utility.
Handles fetching live data from yFinance with an offline fallback
to stocks.csv. Standardizes stock structures for AI pipelines.
"""

import csv
import os

def load_local_stocks():
    """Loads all stocks from stocks.csv and returns a dict mapping ticker -> stock_dict."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'stocks.csv')
    stocks = {}
    if not os.path.exists(csv_path):
        return stocks
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ticker = row['ticker']
            stocks[ticker] = {
                'ticker': ticker,
                'company': row['company'],
                'sector': row['sector'],
                'market_cap': float(row['market_cap']),
                'pe_ratio': float(row['pe_ratio']),
                'volatility': float(row['volatility']),
                'week_52_high': float(row['week_52_high']),
                'week_52_low': float(row['week_52_low']),
                'avg_volume': float(row['avg_volume']),
                'current_price': (float(row['week_52_high']) + float(row['week_52_low'])) / 2.0,
                'market': row['market']
            }
    return stocks

def fetch_live_stock(ticker, local_fallback):
    """Fetches live stock data using yfinance, falling back to local data if unavailable."""
    try:
        import yfinance as yf
        import numpy as np
        
        info = None
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            pass
            
        hist = yf.Ticker(ticker).history(period="1mo")
        if hist.empty:
            if info and 'regularMarketPrice' in info:
                current_price = float(info['regularMarketPrice'])
            else:
                raise ValueError("No price data available")
        else:
            close_prices = hist['Close'].values
            close_prices = close_prices[~np.isnan(close_prices)]
            if len(close_prices) == 0:
                raise ValueError("No valid close prices")
            current_price = float(close_prices[-1])
            
        # Standardize sector, company name, etc.
        company = local_fallback['company']
        sector = local_fallback['sector']
        market_cap = local_fallback['market_cap']
        pe_ratio = local_fallback['pe_ratio']
        volatility = local_fallback.get('volatility', 0.20)
        week_52_high = local_fallback['week_52_high']
        week_52_low = local_fallback['week_52_low']
        avg_volume = local_fallback['avg_volume']
        
        if info:
            company = info.get('longName', info.get('shortName', company))
            sector = info.get('sector', sector)
            market_cap = float(info.get('marketCap', market_cap))
            pe_ratio = float(info.get('trailingPE', info.get('forwardPE', pe_ratio)))
            week_52_high = float(info.get('fiftyTwoWeekHigh', week_52_high))
            week_52_low = float(info.get('fiftyTwoWeekLow', week_52_low))
            avg_volume = float(info.get('averageVolume', avg_volume))
            
        if not hist.empty and len(close_prices) > 1:
            pct_changes = (close_prices[1:] - close_prices[:-1]) / close_prices[:-1]
            volatility = float(np.std(pct_changes) * np.sqrt(252))
            
        return {
            'ticker': ticker,
            'company': company,
            'sector': sector,
            'market_cap': market_cap,
            'pe_ratio': pe_ratio,
            'volatility': volatility,
            'week_52_high': week_52_high,
            'week_52_low': week_52_low,
            'avg_volume': avg_volume,
            'current_price': current_price,
            'market': local_fallback['market']
        }
    except Exception:
        return local_fallback

def fetch_history(ticker, fallback_price, fallback_vol):
    """Fetches 30-day historical prices or generates simulated fallback prices."""
    try:
        import yfinance as yf
        import numpy as np
        hist = yf.Ticker(ticker).history(period="1mo")
        if not hist.empty:
            hist = hist.dropna(subset=['Close'])
            if not hist.empty:
                return [{'date': d.strftime('%Y-%m-%d'), 'price': float(r['Close'])} for d, r in hist.iterrows()]
    except Exception:
        pass
    import numpy as np
    import datetime
    np.random.seed(hash(ticker) % 1234567)
    days = 22
    prices = [fallback_price]
    for _ in range(days - 1):
        change = np.random.normal(0, fallback_vol / np.sqrt(252))
        prices.append(prices[-1] * (1.0 + change))
    today = datetime.date.today()
    return [{'date': (today - datetime.timedelta(days=i)).strftime('%Y-%m-%d'), 'price': float(p)} 
            for i, p in enumerate(reversed(prices))][::-1]

def update_csv_stock(ticker, updated_data):
    """Updates a single stock's metrics in stocks.csv."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'stocks.csv')
    if not os.path.exists(csv_path):
        return
        
    stocks = []
    fieldnames = ['ticker', 'company', 'sector', 'market_cap', 'pe_ratio', 'volatility', 'week_52_high', 'week_52_low', 'avg_volume', 'market']
    
    with open(csv_path, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['ticker'] == ticker:
                row['company'] = updated_data.get('company', row['company'])
                row['sector'] = updated_data.get('sector', sector_map := updated_data.get('sector', row['sector']))
                row['market_cap'] = str(updated_data.get('market_cap', row['market_cap']))
                row['pe_ratio'] = str(updated_data.get('pe_ratio', row['pe_ratio']))
                row['volatility'] = str(updated_data.get('volatility', row['volatility']))
                
                high = updated_data.get('week_52_high', row['week_52_high'])
                row['week_52_high'] = f"{high:.2f}" if isinstance(high, float) else str(high)
                
                low = updated_data.get('week_52_low', row['week_52_low'])
                row['week_52_low'] = f"{low:.2f}" if isinstance(low, float) else str(low)
                
                row['avg_volume'] = str(updated_data.get('avg_volume', row['avg_volume']))
            stocks.append(row)
            
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stocks)

