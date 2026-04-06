import requests
import time
from datetime import datetime

# The wallet address you want to monitor
TARGET_WALLET = "0xb066420c951615bbda3cee4092b6c06b1a1ca0d7"

# Polymarket CLOB API endpoint for trade fills
API_URL = "https://clob.polymarket.com/fills"

def get_latest_trades(address):
    """Fetches the most recent trade fills for a specific address."""
    params = {
        "user": address,
        "limit": 5  # Fetch the last 5 to ensure we don't miss rapid-fire trades
    }
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status {response.status_code}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []

def run_monitor():
    print(f"--- Monitoring Wallet: {TARGET_WALLET} ---")
    print("Scanning for new trades every second...\n")
    
    seen_trade_ids = set()
    
    # Initialize seen trades so we only report NEW ones starting now
    initial_trades = get_latest_trades(TARGET_WALLET)
    for trade in initial_trades:
        seen_trade_ids.add(trade.get('id'))

    while True:
        trades = get_latest_trades(TARGET_WALLET)
        
        for trade in reversed(trades): # Process oldest to newest
            trade_id = trade.get('id')
            
            if trade_id not in seen_trade_ids:
                # Extract trade details
                side = trade.get('side')  # BUY or SELL
                price = trade.get('price')
                size = trade.get('size')
                market = trade.get('asset_id') # The unique ID for the outcome
                timestamp = datetime.now().strftime("%H:%M:%S")

                print(f"[{timestamp}] NEW TRADE DETECTED")
                print(f"  Side:   {side}")
                print(f"  Price:  ${price}")
                print(f"  Size:   {size} shares")
                print(f"  Market: {market}")
                print("-" * 30)

                seen_trade_ids.add(trade_id)
        
        # Limit the size of the 'seen' set to prevent memory issues over time
        if len(seen_trade_ids) > 100:
            seen_trade_ids = set(list(seen_trade_ids)[-50:])

        time.sleep(1) # Wait 1 second before checking again

if __name__ == "__main__":
    run_monitor()
