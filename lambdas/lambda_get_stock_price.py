import requests
import os
import json

def lambda_handler(event, context):
    symbol = event.get('symbol', 'IBM')
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', 'YOUR_KEY_HERE')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}'
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        timeseries = data.get("Time Series (5min)")
        if not timeseries:
            raise Exception("No time series found or API limit reached")
        # Get most recent timestamp
        latest_time = sorted(timeseries.keys())[-1]
        current_price = timeseries[latest_time]["4. close"]
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": str(e),
                "symbol": symbol,
                "current_price": "N/A"
            })
        }
    return {
        "statusCode": 200,
        "body": json.dumps({
            "symbol": symbol,
            "current_price": current_price
        })
    }
