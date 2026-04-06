import requests
import time
from datetime import datetime

# CONFIGURATION
TARGET_WALLET = "0xb066420c951615bbda3cee4092b6c06b1a1ca0d7"
COPY_RATIO = 0.01  # Calculate as if you are trading 1% of their size
POLL_INTERVAL = 2  # Seconds (Polymarket rate limits Railway IPs if set to 1)

# API ENDPOINT (Updated for 2026 Gamma API)
API_URL = "https://gamma-api.polymarket.com/executions"

def get_trades():
    """Fetches the latest trades for the target wallet."""
    params = {
        "user": TARGET_WALLET,
        "limit": 10
    }
    try:
        # We include a User-Agent so Polymarket doesn't block the Railway request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36"
        }
        response = requests.get(API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print("Error 404: Endpoint moved. Trying fallback v1 CLOB...")
            # Fallback to CLOB v1 if Gamma fails
            fallback_url = "https://clob.polymarket.com/v1/fills"
            return requests.get(fallback_url, params={"user": TARGET_WALLET}, headers=headers).json()
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] API Error {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []

def run_observer():
    print(f"--- Polymarket Observer Initialized ---")
    print(f"Target: {TARGET_WALLET}")
    print(f"Scale: {COPY_RATIO*100}% of original size")
    print("---------------------------------------")

    last_trade_ids = set()
    
    # Pre-fill with current trades so we only alert on NEW ones
    initial_data = get_trades()
    for t in initial_data:
        last_trade_ids.add(t.get('id') or t.get('transaction_hash'))

    while True:
        current_trades = get_trades()
        
        # Process in reverse (oldest to newest)
        for trade in reversed(current_trades):
            trade_id = trade.get('id') or trade.get('transaction_hash')
            
            if trade_id and trade_id not in last_trade_ids:
                # Extraction logic for Gamma/CLOB formats
                side = trade.get('side', 'N/A')
                price = float(trade.get('price', 0))
                size = float(trade.get('size', 0))
                
                # Calculations
                orig_cost = price * size
                your_cost = orig_cost * COPY_RATIO
                
                now = datetime.now().strftime("%H:%M:%S")
                print(f"[{now}] NEW TRADE FOUND:")
                print(f"  Action: {side} @ ${price:.3f}")
                print(f"  Wallet Spent: ${orig_cost:,.2f}")
                print(f"  Your Copy Cost: ${your_cost:,.2f}")
                print(f"  Market ID: {trade.get('asset_id', 'Unknown')}")
                print("-" * 30)
                
                last_trade_ids.add(trade_id)

        # Keep the memory clean
        if len(last_trade_ids) > 100:
            last_trade_ids = set(list(last_trade_ids)[-50:])

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_observer()
