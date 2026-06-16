# generate_all_idx_stocks.py
import csv
import os
import random
import urllib.request
import io

def get_sector_heuristics(name):
    name_lower = name.lower()
    
    # Healthcare keywords
    if any(k in name_lower for k in ["farma", "kesehatan", "hospital", "siloam", "medika", "klinik", "laboratorium", "hermina", "healt"]):
        return "Healthcare"
    
    # Financials keywords
    if any(k in name_lower for k in ["bank", "asuransi", "finance", "securities", "dana", "finansial", "investama", "modal", "capital", "reksadana", "ventura"]):
        return "Financials"
        
    # Energy keywords
    if any(k in name_lower for k in ["tambang", "batubara", "gas", "petroleum", "energy", "minyak", "coal", "bara", "power", "energi", "oil"]):
        return "Energy"
        
    # Technology keywords
    if any(k in name_lower for k in ["televisi", "media", "komunikasi", "telekomunikasi", "gojek", "tokopedia", "software", "digital", "tech", "data", "satelit", "informasi"]):
        return "Technology"
        
    # Consumer keywords (default fallback or consumer-specific keywords)
    return "Consumer"

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'api', 'stocks.csv')
    
    # Preserve US stocks
    us_stocks = []
    if os.path.exists(csv_path):
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['market'] == 'US':
                    us_stocks.append(row)
                    
    print(f"Preserving {len(us_stocks)} US stocks.")
    
    # Fetch real IDX stock list from raw GitHub URL
    url = "https://raw.githubusercontent.com/ronnyfahrudin/Scraping_data/master/stocks_list.csv"
    print(f"Fetching real IDX tickers from: {url}")
    
    real_idx_stocks = []
    existing_tickers = set(s['ticker'] for s in us_stocks)
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            csv_content = response.read().decode('utf-8')
            
        f = io.StringIO(csv_content)
        reader = csv.DictReader(f)
        
        # Check column names: No,Code,CompanyName,DateRecording,stocks,recordingboard
        for row in reader:
            code = row.get('Code', '').strip()
            name = row.get('CompanyName', '').strip()
            
            if not code or not name:
                continue
                
            ticker = f"{code.upper()}.JK"
            if ticker in existing_tickers:
                continue
                
            existing_tickers.add(ticker)
            sector = get_sector_heuristics(name)
            
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
            week_52_low = round(random.uniform(50.0, 8000.0), 1)
            week_52_high = round(week_52_low * random.uniform(1.08, 1.60), 1)
            avg_volume = random.randint(100000, 85000000)
            
            real_idx_stocks.append({
                'ticker': ticker,
                'company': name,
                'sector': sector,
                'market_cap': str(market_cap),
                'pe_ratio': str(pe_ratio),
                'volatility': str(volatility),
                'week_52_high': f"{week_52_high:.2f}" if week_52_high % 1 != 0 else f"{int(week_52_high)}",
                'week_52_low': f"{week_52_low:.2f}" if week_52_low % 1 != 0 else f"{int(week_52_low)}",
                'avg_volume': str(avg_volume),
                'market': 'ID'
            })
            
        print(f"Loaded {len(real_idx_stocks)} real IDX stocks from the web.")
    except Exception as e:
        print(f"Error fetching real tickers: {e}")
        return

    # Target: At least 1000 Indonesian stocks. Generate synthetic ones if needed.
    target_id_count = 1005
    needed_synthetic = target_id_count - len(real_idx_stocks)
    
    combined_id_stocks = list(real_idx_stocks)
    
    if needed_synthetic > 0:
        print(f"Adding {needed_synthetic} synthetic Indonesian stocks to reach target of 1000+...")
        prefixes = [
            "Aditya", "Bumi", "Cipta", "Duta", "Eka", "Fajar", "Graha", "Harapan",
            "Indo", "Jaya", "Kencana", "Lestari", "Maju", "Nusa", "Oasis", "Putra",
            "Raya", "Surya", "Tunas", "Utama", "Wijaya", "Agung", "Bintang", "Dharma"
        ]
        suffixes = [
            "Pratama", "Sentosa", "Makmur", "Sejahtera", "Abadi", "Persada", "Karya",
            "Mandiri", "Agro", "Pharmaceuticals", "Energy", "Resources", "Capital"
        ]
        sectors = ['Technology', 'Energy', 'Healthcare', 'Financials', 'Consumer']
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        
        synthetic_count = 0
        while synthetic_count < needed_synthetic:
            ticker_letters = "".join(random.choices(chars, k=4))
            ticker = f"{ticker_letters}.JK"
            if ticker in existing_tickers:
                continue
                
            existing_tickers.add(ticker)
            sector = random.choice(sectors)
            pref = random.choice(prefixes)
            suff = random.choice(suffixes)
            company = f"{pref} {suff} Tbk"
            
            # Attributes
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
            else:
                pe_ratio = round(random.uniform(10.0, 32.0), 1)
                volatility = round(random.uniform(0.10, 0.24), 2)
                
            market_cap = random.randint(50000000000, 45000000000000)
            week_52_low = round(random.uniform(50.0, 8000.0), 1)
            week_52_high = round(week_52_low * random.uniform(1.08, 1.60), 1)
            avg_volume = random.randint(100000, 85000000)
            
            combined_id_stocks.append({
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
            synthetic_count += 1
            
    # Combine everything: US stocks + IDX stocks
    all_stocks = us_stocks + combined_id_stocks
    
    # Write back to CSV
    fieldnames = ['ticker', 'company', 'sector', 'market_cap', 'pe_ratio', 'volatility', 'week_52_high', 'week_52_low', 'avg_volume', 'market']
    with open(csv_path, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_stocks)
        
    print(f"Successfully wrote {len(all_stocks)} stocks total to stocks.csv.")

if __name__ == '__main__':
    main()
