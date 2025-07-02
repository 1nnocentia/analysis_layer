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

app = FastAPI(
    title="Slither Analysis Service",
    desciption="API untuk analisis statis smart contract dengan slither",
    version="1.0.0"
)

# 3. Helper untuk transformasi output

