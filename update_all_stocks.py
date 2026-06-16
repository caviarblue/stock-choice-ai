# update_all_stocks.py
import os
import sys
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure root folder is in path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.utils.fetcher import load_local_stocks, fetch_live_stock

def update_single_stock(ticker, local_data):
    """Fetches live stock data for a single ticker."""
    live_data = fetch_live_stock(ticker, local_data)
    return ticker, live_data

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'api', 'stocks.csv')
    
    local_stocks = load_local_stocks()
    total = len(local_stocks)
    print(f"Loaded {total} stocks from stocks.csv. Starting bulk update...")
    
    updated_stocks = {}
    completed_count = 0
    
    # Run in parallel using a ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(update_single_stock, ticker, data): ticker for ticker, data in local_stocks.items()}
        
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                ticker, live_data = future.result()
                updated_stocks[ticker] = live_data
            except Exception as e:
                print(f"Error updating {ticker}: {e}")
                updated_stocks[ticker] = local_stocks[ticker]
                
            completed_count += 1
            if completed_count % 50 == 0 or completed_count == total:
                print(f"Progress: [{completed_count}/{total}] stocks updated.")
                
    # Write back to CSV
    fieldnames = ['ticker', 'company', 'sector', 'market_cap', 'pe_ratio', 'volatility', 'week_52_high', 'week_52_low', 'avg_volume', 'market']
    
    ordered_stocks = []
    for ticker in local_stocks:
        data = updated_stocks.get(ticker, local_stocks[ticker])
        
        high = data.get('week_52_high', 0)
        low = data.get('week_52_low', 0)
        
        row = {
            'ticker': data['ticker'],
            'company': data['company'],
            'sector': data['sector'],
            'market_cap': str(data['market_cap']),
            'pe_ratio': str(data['pe_ratio']),
            'volatility': str(data['volatility']),
            'week_52_high': f"{high:.2f}" if isinstance(high, float) else str(high),
            'week_52_low': f"{low:.2f}" if isinstance(low, float) else str(low),
            'avg_volume': str(data['avg_volume']),
            'market': data['market']
        }
        ordered_stocks.append(row)
        
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ordered_stocks)
        
    print(f"Bulk update completed successfully! Saved {len(ordered_stocks)} updated stocks to stocks.csv.")

if __name__ == '__main__':
    main()
