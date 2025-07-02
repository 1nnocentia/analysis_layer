# tarik data pakai FastAPI

import uvicorn # server ASGI (Asynchronous Server Gateway Interface) -> menjalankan FastAPI secra lokal
import subprocess # untuk menjalankan slither dari python
import json # konversi antara py dan json
import tempfile # temporary file
import os # berinteraksi dengan path/env/file system
from fastapi import FastAPI, HTTPException # untuk buat endpoint
from pydantic import BaseModel # class model untuk validasi data (JSON request)
from typing import List # variable type untuk list

# 1. Model data (requst dan response)
# validasi struktur input dan output API

class ContractInput(BaseModel):
    """
    Model untuk data input
    Cek apakah JSON yang diterima bertipe String
    """
    source_code: str

class Issue(BaseModel):
    """
    Model untuk issue yang ditemukan
    @param
    type: jenis issue (string)
    line: nomor baris issue ditemukan (int)
    severity: tingkat keparahan issue (string)
    message: pesan deskriptif tentang issue (string)
    """
    type: str
    line: int
    severity: str
    message: str

class AnalysisResponse(BaseModel):
    """
    Model untuk respon JSON yang dikirim kembali
    @param
    issues: daftar issue yang ditemukan (list of Issue)
    """
    issues: List[Issue]

# 2. Initialize FastAPI
# akan digunakan untuk membuat endpoint API

app = FastAPI(
    title="Slither Analysis Service",
    description="API untuk analisis statis smart contract dengan slither",
    version="1.0.0"
)

# 3. Helper untuk transformasi output

def format_slither_output(slither_row_json: dict) -> List[Issue]:
    """
    Mengubah output JSON dari Slither menjadi format sesuai dengan input di layer setelahnya
    """
    formated_issues = []

    # validasi apakah analisis berhasil
    if not slither_row_json.get("success") or not slither_row_json.get("result", {}).get("detectors"):
        return []
    
    detectors = slither_row_json["result"]["detectors"]

    for detector in detectors:
        # informasi dasar
        issue_type = detector.get("check", "N/A")
        severity = detector.get("impact", "N/A")
        # ambil infromasi dari Slither
        message = detector.get("message", "No message available").split("\n")[0]

        # detektor bisa punya beberapa lokasi
        if "elements" in detector:
            for element in detector["elements"]:
                # ambil nomor baris dari elemen
                line_number = element.get("source_mapping", {}).get("start", {}).get("line", [0])[0]
                
                issue = Issue(
                    type=issue_type,
                    line=line_number,
                    severity=severity,
                    message=message
                )
                formated_issues.append(issue)
    return formated_issues