import json
import os
import requests
import PyPDF2
from io import BytesIO

# ----------- PDF Extraction --------------
def extract_text_from_pdf(pdf_url):
    """Downloads the PDF and extracts text (first 4000 chars)."""
    try:
        res = requests.get(pdf_url, timeout=10)
        res.raise_for_status()
        reader = PyPDF2.PdfReader(BytesIO(res.content))
        all_text = ""
        for page in reader.pages:
            text = page.extract_text() or ""
            all_text += text
        # Limit to first 4000 chars for prompt/model size safety
        return all_text[:4000]
    except Exception as e:
        raise Exception(f"PDF extraction error: {e}")

# ----------- API Calls --------------
def get_finnhub_quote(ticker, api_key):
    """Get real-time quote from Finnhub.io."""
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
    r = requests.get(url)
    # TODO: Handle special cases (rate limit, errors)
    return r.json() if r.ok else {"error": r.text}

def get_alphavantage_history(ticker, api_key):
    """Fetch 5 recent daily closes from AlphaVantage."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}"
    r = requests.get(url)
    # TODO: Better error handling for rate limits, invalid symbol, etc.
    return r.json() if r.ok else {"error": r.text}

# ----------- Data Merge --------------
def merge_data(upload_text, finnhub, alphavantage):
    """Extracts recent prices and merges with doc extract."""
    closes = []
    days = []
    if "Time Series (Daily)" in alphavantage:
        series = alphavantage["Time Series (Daily)"]
        days = list(series.keys())[:5]
        closes = [series[d]["4. close"] for d in days]
    merged = {
        "uploaded_doc_brief": upload_text[:400],  # Only the start (for summary preview)
        "latest_price": finnhub.get("c"),
        "today_high": finnhub.get("h"),
        "today_low": finnhub.get("l"),
        "historical_days": days,
        "historical_closes": closes,
        # Add more metrics for in-depth comparisons if desired
    }
    return merged

# ----------- Lambda Handler --------------
def lambda_handler(event, context):
    """
    Inputs:
        - report_url: S3 or public URL of user-uploaded report
        - ticker: e.g. "AAPL"
    Output:
        - answer: A combined, plain-English summary
        - merged: structured merged data
    """
    pdf_url = event.get("report_url")
    ticker = event.get("ticker")

    # Set your API keys securely as Lambda environment variables!
    fh_key = os.environ["FINNHUB_API_KEY"]  # <-- CHANGE: Add this as Lambda env var
    av_key = os.environ["ALPHAVANTAGE_API_KEY"]  # <-- CHANGE: Add this as Lambda env var

    if not pdf_url or not ticker:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing report_url or ticker."})
        }
    try:
        # A. Extract PDF
        doc_text = extract_text_from_pdf(pdf_url)
        # B. Fetch market data from APIs
        finnhub_data = get_finnhub_quote(ticker, fh_key)
        alphavantage_data = get_alphavantage_history(ticker, av_key)
        # C. Merge both datasets
        merged_info = merge_data(doc_text, finnhub_data, alphavantage_data)
        # D. Build human-readable answer
        answer = (
            f"**Document Extract (truncated):**\n{merged_info['uploaded_doc_brief']}\n\n"
            f"**Latest Price for {ticker}:** {merged_info['latest_price']}\n"
            f"**Today's High:** {merged_info['today_high']} | **Low:** {merged_info['today_low']}\n"
            "**Recent Daily Closes:**\n"
        )
        for idx, date in enumerate(merged_info["historical_days"]):
            close = merged_info["historical_closes"][idx]
            answer += f"{date}: ${close}\n"

        return {"statusCode": 200, "body": json.dumps({"answer": answer, "merged": merged_info})}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
