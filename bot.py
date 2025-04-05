# -*- coding: utf-8 -*-
import os
import time
import ccxt
import sys
import io
from openai import OpenAI
from dotenv import load_dotenv

# Safe UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='ignore')

# Load .env
load_dotenv()

# Safe print helper
def safe_print(label, value):
    try:
        print(label, str(value))
    except Exception as e:
        print(label, "Print error:", repr(e))

# API Key check
print("Checking API keys...")
safe_print("OpenAI Key:", os.getenv("OPENAI_API_KEY"))
safe_print("Bitget Key:", os.getenv("BITGET_API_KEY"))
safe_print("Bitget Secret:", os.getenv("BITGET_SECRET_KEY"))

# Set up clients
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
exchange = ccxt.bitget({
    "apiKey": os.getenv("BITGET_API_KEY"),
    "secret": os.getenv("BITGET_SECRET_KEY")
})

# Market data fetch
def get_market_data():
    try:
        print("Fetching market data...")
        candles = exchange.fetch_ohlcv("BTC/USDT", timeframe='1m')
        print("Recent candles:", candles[-3:])
        close_price = candles[-1][4]
        print("Close price:", close_price)
        return close_price
    except Exception as e:
        error_msg = repr(e).encode('ascii', 'ignore').decode('ascii')
        print("Market data error:", error_msg)
        return None

# Smart Money Prompt 전략 통합
def generate_smart_prompt(price):
    return f"""
Current BTC price is {price}.

Please evaluate the following:
1. Did price sweep liquidity below key zones recently?
2. Was there a fakeout above resistance or below support?
3. Is there any recent Break of Structure?
4. Is current price retesting a known order block zone?
5. Did volume spike followed by rejection?

Based on smart money concepts and institutional behavior, should we go long or short?
"""

# GPT 시그널 요청
def get_signal(price):
    prompt = generate_smart_prompt(price)
    print("Sending prompt to GPT...")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=10
        )
        raw = str(response.choices[0].message.content).strip()
        safe = raw.encode('ascii', 'ignore').decode('ascii')
        print("GPT Response:", safe)
        return safe
    except Exception as e:
        error_msg = repr(e).encode('ascii', 'ignore').decode('ascii')
        print("GPT Error:", error_msg)
        return "no signal"

# Trade logic
def execute_trade(signal):
    sig = signal.lower()
    if "long" in sig:
        print("LONG POSITION ENTERED")
    elif "short" in sig:
        print("SHORT POSITION ENTERED")
    else:
        print("NO CLEAR SIGNAL")

# Main loop
print("\nStarting BTC trading bot with Smart Money strategy...\n")

while True:
    print("\n--- NEW CYCLE ---")
    price = get_market_data()
    if price:
        signal = get_signal(price)
        execute_trade(signal)
    else:
        print("Price not available.")
    print("Waiting 60 seconds...\n")
    time.sleep(60)
