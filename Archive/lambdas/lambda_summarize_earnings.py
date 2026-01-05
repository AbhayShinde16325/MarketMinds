import json
import requests
import PyPDF2
from io import BytesIO

def extract_text_from_pdf(pdf_url):
    pdf_response = requests.get(pdf_url)
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_response.content))
    full_text = ""
    for page in pdf_reader.pages:
        full_text += page.extract_text() or ""
    return full_text[:1500]  # Truncate for summarization input

def lambda_handler(event, context):
    report_url = event.get('report_url', '')
    HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
    HF_API_TOKEN = "YOUR_HF_API_TOKEN"  # Get from huggingface.co
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    try:
        pdf_text = extract_text_from_pdf(report_url)
        if not pdf_text or len(pdf_text) < 50:
            raise Exception("PDF text extraction failed or text too short.")

        response = requests.post(HF_API_URL, headers=headers, json={"inputs": pdf_text})
        summary_json = response.json()
        if isinstance(summary_json, list) and "summary_text" in summary_json[0]:
            summary = summary_json[0]["summary_text"]
        else:
            summary = "NLP summarization failed."

        result = {"summary": summary}
        status_code = 200
    except Exception as e:
        result = {
            "error": str(e),
            "summary": "N/A"
        }
        status_code = 500

    return {
        "statusCode": status_code,
        "body": json.dumps(result)
    }
