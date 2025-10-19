import json
import os
import requests
import PyPDF2
from io import BytesIO

def extract_financial_fields_from_pdf(pdf_url):
    """
    Extracts text from uploaded PDF report.
    TODO: For deeper implementations, parse specific fields (revenue, profit, etc). 
    """
    try:
        res = requests.get(pdf_url, timeout=10)
        res.raise_for_status()
        reader = PyPDF2.PdfReader(BytesIO(res.content))
        all_text = ""
        for page in reader.pages:
            all_text += page.extract_text() or ""
        # Limit to first 4000 chars for prompt/model safety
        return all_text[:4000]
    except Exception as e:
        raise Exception(f"PDF extraction error: {e}")

def get_finnhub_quote(ticker, api_key):
    """Get real-time quote from Finnhub."""
    url = f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}"
    r = requests.get(url)
    return r.json() if r.ok else {"error": r.text}

def get_alphavantage_history(ticker, api_key):
    """Fetch recent daily closes from AlphaVantage."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}"
    r = requests.get(url)
    return r.json() if r.ok else {"error": r.text}

def get_closing_prices(av_data, days=30):
    """Returns (dates, closes) arrays for most recent `days` history."""
    closes, dates = [], []
    if "Time Series (Daily)" in av_data:
        series = av_data["Time Series (Daily)"]
        for d, v in list(series.items())[:days]:
            closes.append(float(v["4. close"]))
            dates.append(d)
    return dates[::-1], closes[::-1]  # Reverse so X-axis is old→new

def predict_with_llm(prompt, hf_token):
    """
    Calls HuggingFace Inference API for LLM-based numeric+explanation.
    For production: Prefer Bedrock, SageMaker, or private LLM endpoint.
    """
    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-70b-chat-hf"
    headers = {"Authorization": f"Bearer {hf_token}"}
    resp = requests.post(url, headers=headers, json={"inputs": prompt})
    if resp.status_code == 200:
        out = resp.json()
        # For HF, response is a list with "generated_text"
        if isinstance(out, list) and "generated_text" in out[0]:
            return out[0]["generated_text"]
        elif isinstance(out, dict) and "generated_text" in out:
            return out["generated_text"]
        return str(out)
    return f"Prediction error: {resp.text}"

def lambda_handler(event, context):
    """
    Required event params:
        - report_url: S3 or public URL of report (PDF)
        - ticker: e.g. "AAPL"
        - user_query: Natural-language prediction task
    Output:
        - llm_answer: Predictive numeric + explanatory, from LLM
        - chart_data: {dates, close_prices, predicted_label}
    """
    pdf_url = event.get("report_url")
    ticker = event.get("ticker")
    user_request = event.get("user_query")
    fh_key = os.environ["FINNHUB_API_KEY"]
    av_key = os.environ["ALPHAVANTAGE_API_KEY"]
    hf_token = os.environ.get("HF_API_TOKEN", "YOUR_HF_TOKEN")

    if not pdf_url or not ticker or not user_request:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields (report_url, ticker, user_query)."})}
    try:
        # 1. Extract document (basic text for now, see TODO)
        doc_text = extract_financial_fields_from_pdf(pdf_url)

        # 2. Fetch API data for ticker
        finnhub = get_finnhub_quote(ticker, fh_key)
        av = get_alphavantage_history(ticker, av_key)
        dates, closes = get_closing_prices(av, days=30)

        # 3. Build LLM prompt for prediction+explanation
        llm_prompt = (
            f"Based on this financial report and current + recent stock data, answer this:\n"
            f"---\nDocument Extract: {doc_text[:500]} ...\n"
            f"Recent closing prices (past 5): {closes[-5:]}\n"
            f"Current price: {finnhub.get('c')}\n"
            f"User request: {user_request}\n"
            f"Provide a numeric prediction, explain your reasoning, and cite key indicators used.\n"
        )
        llm_answer = predict_with_llm(llm_prompt, hf_token)

        chart_data = {
            "dates": dates,
            "close_prices": closes,
            "predicted_label": user_request
        }
        return {
            "statusCode": 200,
            "body": json.dumps({
                "llm_answer": llm_answer,
                "chart_data": chart_data
            })
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
