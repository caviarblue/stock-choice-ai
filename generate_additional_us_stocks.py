# generate_additional_us_stocks.py
import csv
import os
import random

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'api', 'stocks.csv')
    
    # Read existing stocks
    all_stocks = []
    existing_tickers = set()
    
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_stocks.append(row)
                existing_tickers.add(row['ticker'])
                
    us_stocks_count = sum(1 for s in all_stocks if s['market'] == 'US')
    print(f"Loaded {len(all_stocks)} stocks total ({us_stocks_count} US stocks, {len(all_stocks) - us_stocks_count} Indonesian stocks).")
    
    # Target: Generate 200 more US stocks
    needed_us_stocks = 200
    print(f"Generating {needed_us_stocks} additional US stocks...")
    
    prefixes = [
        "Apex", "Horizon", "United", "General", "American", "National", "Pacific",
        "Standard", "Western", "Eastern", "Alliance", "Premier", "Vanguard", "Summit",
        "Beacon", "Pioneer", "Liberty", "Matrix", "Global", "Alpha", "Omni", "Core",
        "Crown", "Delta", "Eclipse", "Genesis", "Infinity", "Legacy", "Nova", "Orion",
        "Quantum", "Sierra", "Trident", "Vector", "Zenith", "Aero", "Bio", "Eco"
    ]
    
    suffixes = [
        "Technologies", "Energy", "Healthcare", "Financial", "Retail", "Industries",
        "Group", "Systems", "Corp", "Inc.", "Partners", "Holdings", "Solutions",
        "Ventures", "Networks", "Labs", "Communications", "Therapeutics", "Power",
        "Resources", "Capital", "Logistics", "Brands", "Dynamics", "Security"
    ]
    
    sectors = ['Technology', 'Energy', 'Healthcare', 'Financials', 'Consumer']
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    generated_count = 0
    while generated_count < needed_us_stocks:
        # Generate a unique 3-4 letter ticker symbol (US format)
        ticker_len = random.choice([3, 4])
        ticker = "".join(random.choices(chars, k=ticker_len))
        
        if ticker in existing_tickers:
            continue
            
        existing_tickers.add(ticker)
        sector = random.choice(sectors)
        pref = random.choice(prefixes)
        suff = random.choice(suffixes)
        company = f"{pref} {suff}"
        
        # Sector-specific attributes in USD
        if sector == 'Technology':
            pe_ratio = round(random.uniform(20.0, 75.0), 1)
            volatility = round(random.uniform(0.18, 0.45), 2)
            week_52_low = round(random.uniform(10.0, 1000.0), 2)
        elif sector == 'Financials':
            pe_ratio = round(random.uniform(8.0, 22.0), 1)
            volatility = round(random.uniform(0.10, 0.22), 2)
            week_52_low = round(random.uniform(10.0, 450.0), 2)
        elif sector == 'Energy':
            pe_ratio = round(random.uniform(4.0, 14.0), 1)
            volatility = round(random.uniform(0.15, 0.32), 2)
            week_52_low = round(random.uniform(10.0, 180.0), 2)
        elif sector == 'Healthcare':
            pe_ratio = round(random.uniform(15.0, 40.0), 1)
            volatility = round(random.uniform(0.12, 0.26), 2)
            week_52_low = round(random.uniform(10.0, 800.0), 2)
        else: # Consumer
            pe_ratio = round(random.uniform(10.0, 32.0), 1)
            volatility = round(random.uniform(0.08, 0.22), 2)
            week_52_low = round(random.uniform(10.0, 350.0), 2)
            
        market_cap = random.randint(3000000000, 1500000000000) # 3B to 1.5T USD
        week_52_high = round(week_52_low * random.uniform(1.08, 1.55), 2)
        avg_volume = random.randint(500000, 45000000)
        
        all_stocks.append({
            'ticker': ticker,
            'company': company,
            'sector': sector,
            'market_cap': str(market_cap),
            'pe_ratio': str(pe_ratio),
            'volatility': str(volatility),
            'week_52_high': f"{week_52_high:.2f}",
            'week_52_low': f"{week_52_low:.2f}",
            'avg_volume': str(avg_volume),
            'market': 'US'
        })
        
        generated_count += 1
        
    # Write back to CSV
    fieldnames = ['ticker', 'company', 'sector', 'market_cap', 'pe_ratio', 'volatility', 'week_52_high', 'week_52_low', 'avg_volume', 'market']
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_stocks)
        
    print(f"Successfully added 200 US stocks. Total stocks database size is now: {len(all_stocks)}.")

if __name__ == '__main__':
    main()
