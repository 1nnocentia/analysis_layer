"""
Analysis Service Layer 2 (LLM):
1. Analisa secara menyeluruh
2. Menghitung Risk Score
3. Menghasilkan penjelasan (summary)
"""

import uvicorn
import os
import json
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field
from typing import List
import requests 
import logging


# buat logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# 1. Input data sesuai output dari layer 1
class Issue(BaseModel):
    type: str
    line: int
    severity: str
    message: str

class AnalysisInput(BaseModel):
    issues: List[Issue]

class LLMReportResponse(BaseModel):
    risk_summary: str = Field(..., description="Ringkasan risiko menyeluruh secara singkat")
    llm_recommendation: str = Field(..., description="Rekomendasi perbaikan")
    risk_grading: str = Field(..., description="Grading risiko menyeluruh")
    confidence_score: float = Field(..., ge=0, le=1,description="Confidence score analisa")

# 2. Initialize FastAPI

app = FastAPI(
    title="LLM Analysis Service",
    description="Layer Analisis kedua untuk laporan analisa",
    version="1.2.0",
)

# 3. helper

def create_llm_prompt(issues: List[Issue]) -> str:
    """
    Prompting untuk mendapatkan analisa dari LLM
    """
    if not issues:
        return "Tidak ada risiko yang ditemukan. Konfirmasi jika smartcontract aman."

    prompt_header = "Kamu adalah seorang auditor smart contract yang ahli. Kamu akan menerima laporan analisis dari Slither atau Mythril. Analisislah temuan-temuan berikut ini dengan pendekatan yang holistik, berdasarkan hasil temuan berikut:\n\n"

    issue_details = ""
    for issue in issues:
        issue_details += (
            f"Jenis Kerentanan: {issue.type}\n"
            f"Tingkat Keparahan: {issue.severity}\n"
            f"Baris/Lokasi: {issue.line}\n"
            f"Pesan: {issue.message}\n\n"
        )

    prompt_footer = (
        "\n Berdasarkan semua temuan di atas, silakan berikan analisismu. JAWABANMU HARUS BERUPA OBJEK JSON YANG VALID, dan HANYA berupa objek JSON yang valid, dengan struktur sebagai berikut:\n" 
        "'risk_summary': 'Ringkasan risiko secara holistik dalam 1-2 kalimat.',\n"
        "'llm_recommendation': 'Rekomendasi perbaikan yang paling penting dan dapat segera dilakukan.',\n"
        "'risk_grading': 'Penilaian risiko dalam satu kata: Kritis, Tinggi, Sedang, atau Rendah.',\n"
        "'confidence_score': 'Angka desimal antara 0.0 hingga 1.0 yang merepresentasikan tingkat keyakinan (confidence)'\n"
    )
    return prompt_header + issue_details + prompt_footer

# 4. endpoint

@app.post("/generate-report", response_model=LLMReportResponse, summary="Laporan Analisis")
async def generate_report(analysis_input: AnalysisInput):
    """
    Terima input, kirim ke LLM, hasil: laporan analisis
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment variables")
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY not set in environment variables")
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"

    prompt = create_llm_prompt(analysis_input.issues)
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.2,
        }
    }

    try:
        logger.info("Sending request to LLM API")
        response = requests.post(api_url, json=payload, timeout=60)
        response.raise_for_status() 

        response_json = response.json()

        report_text = response_json['candidates'][0]['content']['parts'][0]['text']
        
        report_data = json.loads(report_text)
        logger.info("LLM response received and parsed successfully")

        return LLMReportResponse(**report_data)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to call LLM API: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Failed to call LLM API: {str(e)}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error(f"Failed to parse LLM response: {str(e)}. Response: {response.text}")
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response: {str(e)}. Response: {response.text}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during LLM analysis. {type(e).__name__} - {e}")
    
# 5. run run

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)