import requests
import time
from datetime import datetime

# CONFIG
TARGET_WALLET = "0xb066420c951615bbda3cee4092b6c06b1a1ca0d7"
COPY_RATIO = 0.01 
# 3 seconds is safer for Railway to avoid "Line 1 Column 1" errors
POLL_INTERVAL = 3 

# 2026 Direct CLOB Endpoint
API_URL = "https://clob.polymarket.com/v1/fills"

def get_trades():
    params = {"user": TARGET_WALLET}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
    try:
        response = requests.get(API_URL, params=params, headers=headers, timeout=15)
        
        # This handles the "Line 1 Column 1" error by checking if content exists
        if response.status_code == 200 and response.text.strip():
            return response.json()
        else:
            return []
    except Exception:
        # Silently fail and retry next loop to keep the bot running
        return []

def run():
    print(f"--- Monitoring: {TARGET_WALLET} ---")
    seen_ids = set()
    
    # Get initial trades to avoid spamming old history
    initial = get_trades()
    for t in initial:
        seen_ids.add(t.get('id'))

    while True:
        trades = get_latest = get_trades()
        
        for trade in reversed(trades):
            t_id = trade.get('id')
            if t_id not in seen_ids:
                side = trade.get('side')
                price = float(trade.get('price'))
                size = float(trade.get('size'))
                
                # Calculate costs
                wallet_usd = price * size
                your_usd = wallet_usd * COPY_RATIO
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {side} @ ${price}")
                print(f" > Wallet spent: ${wallet_usd:,.2f} | Your copy: ${your_usd:,.2f}")
                print("-" * 20)
                seen_ids.add(t_id)

        if len(seen_ids) > 200:
            seen_ids = set(list(seen_ids)[-100:])
            
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
    
