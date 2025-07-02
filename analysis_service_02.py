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

#2. Initialize FastAPI

app = FastAPI(
    title="LLM Analysis Service",
    description="Layer Analisis kedua untuk laporan analisa",
    version="1.0.0",
)

