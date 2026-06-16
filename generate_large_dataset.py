# generate_large_dataset.py
import csv
import os
import random

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'api', 'stocks.csv')
    
    # Read existing stocks to preserve them
    existing_stocks = []
    existing_tickers = set()
    
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_stocks.append(row)
                existing_tickers.add(row['ticker'])
                
    id_stocks_count = sum(1 for s in existing_stocks if s['market'] == 'ID')
    print(f"Loaded {len(existing_stocks)} existing stocks ({id_stocks_count} Indonesian, {len(existing_stocks) - id_stocks_count} US).")
    
    # Target: At least 1000 Indonesian stocks
    target_id_stocks = 1005
    needed_id_stocks = target_id_stocks - id_stocks_count
    
    if needed_id_stocks <= 0:
        print("Dataset already contains at least 1000 Indonesian stocks.")
        return
        
    print(f"Generating {needed_id_stocks} additional Indonesian stocks...")
    
    # Word lists for generating realistic Indonesian company names
    prefixes = [
        "Aditya", "Bumi", "Cipta", "Duta", "Eka", "Fajar", "Graha", "Harapan",
        "Indo", "Jaya", "Kencana", "Lestari", "Maju", "Nusa", "Oasis", "Putra",
        "Raya", "Surya", "Tunas", "Utama", "Wijaya", "Agung", "Bintang", "Dharma",
        "Elang", "Giri", "Harta", "Intan", "Karya", "Mega", "Pakar", "Prima",
        "Restu", "Sinar", "Trisula", "Wira", "Zaman", "Artha", "Buana", "Cakra",
        "Dewata", "Gemilang", "Jagad", "Mitra", "Nusantara", "Pertiwi", "Samudra"
    ]
    
    suffixes = [
        "Pratama", "Sentosa", "Makmur", "Sejahtera", "Abadi", "Persada", "Karya",
        "Mandiri", "Agro", "Pharmaceuticals", "Energy", "Resources", "Capital",
        "Financindo", "Tech", "Lestari", "Investama", "Tunggal", "Nusa", "Jaya",
        "Global", "Sejati", "Utama", "Mulia", "Sentra", "Tbk", "Steel", "Food",
        "Logistics", "Media", "Property", "Mining", "Mineral", "Chemical", "Semen"
    ]
    
    sectors = ['Technology', 'Energy', 'Healthcare', 'Financials', 'Consumer']
    
    # Generate unique 4-letter tickers
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    generated_count = 0
    
    while generated_count < needed_id_stocks:
        # Generate random 4-letter ticker
        ticker_letters = "".join(random.choices(chars, k=4))
        ticker = f"{ticker_letters}.JK"
        
        if ticker in existing_tickers:
            continue
            
        existing_tickers.add(ticker)
        
        # Select sector and generate name
        sector = random.choice(sectors)
        pref = random.choice(prefixes)
        suff = random.choice(suffixes)
        
        # Ensure company name sounds somewhat realistic and ends with Tbk
        if suff == "Tbk":
            company = f"{pref} {random.choice(suffixes)} Tbk"
        else:
            company = f"{pref} {suff} Tbk"
            
        # Sector-specific attributes
        if sector == 'Technology':
            pe_ratio = round(random.uniform(20.0, 75.0), 1)
            volatility = round(random.uniform(0.30, 0.55), 2)
        elif sector == 'Financials':
            pe_ratio = round(random.uniform(8.0, 22.0), 1)
            volatility = round(random.uniform(0.11, 0.22), 2)
        elif sector == 'Energy':
            pe_ratio = round(random.uniform(4.0, 14.0), 1)
            volatility = round(random.uniform(0.20, 0.38), 2)
        elif sector == 'Healthcare':
            pe_ratio = round(random.uniform(15.0, 40.0), 1)
            volatility = round(random.uniform(0.14, 0.28), 2)
        else: # Consumer
            pe_ratio = round(random.uniform(10.0, 32.0), 1)
            volatility = round(random.uniform(0.10, 0.24), 2)
            
        market_cap = random.randint(50000000000, 45000000000000) # 50B to 45T IDR
        
        # Price: low between 50 and 8000 IDR
        week_52_low = round(random.uniform(50.0, 8000.0), 1)
        week_52_high = round(week_52_low * random.uniform(1.08, 1.60), 1)
        avg_volume = random.randint(100000, 85000000)
        
        existing_stocks.append({
            'ticker': ticker,
            'company': company,
            'sector': sector,
            'market_cap': str(market_cap),
            'pe_ratio': str(pe_ratio),
            'volatility': str(volatility),
            'week_52_high': f"{week_52_high:.2f}" if week_52_high % 1 != 0 else f"{int(week_52_high)}",
            'week_52_low': f"{week_52_low:.2f}" if week_52_low % 1 != 0 else f"{int(week_52_low)}",
            'avg_volume': str(avg_volume),
            'market': 'ID'
        })
        
        generated_count += 1
        
    # Write all back to CSV
    fieldnames = ['ticker', 'company', 'sector', 'market_cap', 'pe_ratio', 'volatility', 'week_52_high', 'week_52_low', 'avg_volume', 'market']
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_stocks)
        
    print(f"Successfully generated database with {len(existing_stocks)} stocks total.")

if __name__ == '__main__':
    main()
