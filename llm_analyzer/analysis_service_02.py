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

# 1. Input data sesuai output dari layer 1
class Issue(BaseModel):
    type: str
    line: int
    severity: str
    message: str

class AnalysisInput(BaseModel):
    risk_summary: str = Field(..., description="Ringkasan risiko menyeluruh secara singkat")
    llm_recomendation: str = Field(..., description="Rekomendasi perbaikan")
    risk_grading: str = Field(..., description="Grading risiko menyeluruh")
    confidence_score: float = Field(..., description="Confidence score analisa")

# 2. Initialize FastAPI

app = FastAPI(
    title="LLM Analysis Service",
    description="Layer Analisis kedua untuk laporan analisa",
    version="1.0.0",
)

# 3. helper

def create_llm_prompt(issues: List[Issue]) -> str:
    """
    Prompting untuk mendapatkan analisa dari LLM
    """
    if not issues:
        return "Tidak ada risiko yang ditemukan. Konfirmasi jika smartcontract aman."

    prompt_header = "You're a expert smartcontrct auditor. You'll be get the analysis report from either Slither or Mythril. Analyze the following issues with holistic approach, from this following findings:\n\n"

    issue_details = ""
    for issue in issues:
        issue_details += (
            f"Tipe Kerentanan: {issue.type}\n"
            f"Tingkat Keparahan: {issue.severity}\n"
            f"Lokasi: {issue.line}\n"
            f"Pesan: {issue.message}\n\n"
        )

    prompt_footer = (
        "\n Based on all the above findings, please provide your analysis. YOUR RESPONSE MUST BE A VALID JSON OBJECT, and ONLY A VALID JSON object, with the following structure:\n" 
        "'risk_summary': 'Holistic risk summary in 1-2 sentences.',\n"
        "'llm_recommendation': 'The most important and actionable improvement recommendations.',\n"
        "'risk_grading': 'One word risk assessment: Critical, High, Medium, or Low.',\n"
        "'confidence_score': 'A float number between 0.0 and 1.0 that represents your confidence.'\n"
    )
    return prompt_header + issue_details + prompt_footer