"""
Database Module.
Manages SQLite storage for user sessions and stock recommendations.
Includes fallback to /tmp for Vercel serverless environment support.
"""

import sqlite3
import os

def get_db_path():
    """Returns the writable path for the SQLite database."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'database.db')
    # Use /tmp on Vercel (read-only filesystem)
    if os.environ.get('VERCEL') or not os.access(base_dir, os.W_OK):
        db_path = '/tmp/database.db'
    return db_path

def get_connection():
    """Creates a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE,
                risk_level TEXT,
                budget REAL,
                sector TEXT,
                market TEXT DEFAULT 'US'
            )
        ''')
        # Graceful migration for existing databases
        try:
            conn.execute('ALTER TABLE users ADD COLUMN market TEXT DEFAULT "US"')
        except sqlite3.OperationalError:
            pass
        conn.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                ticker TEXT,
                match_score REAL,
                prediction TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                ticker TEXT PRIMARY KEY,
                company TEXT,
                sector TEXT,
                market_cap REAL,
                pe_ratio REAL,
                volatility REAL,
                week_52_high REAL,
                week_52_low REAL,
                avg_volume REAL,
                current_price REAL,
                market TEXT
            )
        ''')
        conn.commit()

def save_session(session_id, risk_level, budget, sector, market):
    """Saves or updates user preference profile for a session."""
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO users (session_id, risk_level, budget, sector, market)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                risk_level=excluded.risk_level,
                budget=excluded.budget,
                sector=excluded.sector,
                market=excluded.market
        ''', (session_id, risk_level, budget, sector, market))
        conn.commit()

def save_recommendation(session_id, ticker, match_score, prediction):
    """Saves a single recommendation item to the database."""
    with get_connection() as conn:
        conn.execute('''
            INSERT INTO recommendations (session_id, ticker, match_score, prediction)
            VALUES (?, ?, ?, ?)
        ''', (session_id, ticker, match_score, prediction))
        conn.commit()

def get_history(session_id):
    """Retrieves all past recommendations for a given session ID."""
    with get_connection() as conn:
        cursor = conn.execute('''
            SELECT ticker, match_score, prediction, timestamp
            FROM recommendations
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))
        return [dict(row) for row in cursor.fetchall()]

def clear_history(session_id):
    """Deletes all recommendations for a given session ID."""
    with get_connection() as conn:
        conn.execute('DELETE FROM recommendations WHERE session_id = ?', (session_id,))
        conn.commit()

def db_seed_stocks_if_empty(csv_stocks):
    """Seeds the stocks table from the baseline stocks if it is currently empty."""
    with get_connection() as conn:
        cursor = conn.execute('SELECT COUNT(*) FROM stocks')
        count = cursor.fetchone()[0]
        if count == 0:
            conn.executemany('''
                INSERT INTO stocks (
                    ticker, company, sector, market_cap, pe_ratio,
                    volatility, week_52_high, week_52_low, avg_volume,
                    current_price, market
                ) VALUES (
                    :ticker, :company, :sector, :market_cap, :pe_ratio,
                    :volatility, :week_52_high, :week_52_low, :avg_volume,
                    :current_price, :market
                )
            ''', list(csv_stocks.values()))
            conn.commit()

def db_load_stocks():
    """Loads all stocks from the SQLite database."""
    with get_connection() as conn:
        cursor = conn.execute('SELECT * FROM stocks')
        stocks = {}
        for row in cursor.fetchall():
            s = dict(row)
            stocks[s['ticker']] = s
        return stocks

def db_update_stock(ticker, updated_data):
    """Updates a single stock's metrics in the SQLite database."""
    with get_connection() as conn:
        conn.execute('''
            UPDATE stocks SET
                company = COALESCE(?, company),
                sector = COALESCE(?, sector),
                market_cap = COALESCE(?, market_cap),
                pe_ratio = COALESCE(?, pe_ratio),
                volatility = COALESCE(?, volatility),
                week_52_high = COALESCE(?, week_52_high),
                week_52_low = COALESCE(?, week_52_low),
                avg_volume = COALESCE(?, avg_volume),
                current_price = COALESCE(?, current_price),
                market = COALESCE(?, market)
            WHERE ticker = ?
        ''', (
            updated_data.get('company'),
            updated_data.get('sector'),
            updated_data.get('market_cap'),
            updated_data.get('pe_ratio'),
            updated_data.get('volatility'),
            updated_data.get('week_52_high'),
            updated_data.get('week_52_low'),
            updated_data.get('avg_volume'),
            updated_data.get('current_price'),
            updated_data.get('market'),
            ticker
        ))
        conn.commit()

