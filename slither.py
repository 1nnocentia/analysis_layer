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

# 4. Buat Endpoint
@app.post("/analyze", response_model=AnalysisResponse, summary="Analisis Kode SmartContract")
async def analyze_contract(contract: ContractInput):
    """
    Endpoint untuk dapat input (source_code), analisa Slither, lalu outputnya daftar issue
    """
    # simpan file code sementara
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sol", delete=False) as tmp_file:
        tmp_file.write(contract.source_code)
        tmp_file_path = tmp_file.name

    try:
        # jalankan Slither dengan subprocess
        # --json, kembalikan output dalam format JSON
        command = ["slither", tmp_file_path, "--json", "-"]

        # eksekusi command
        # cek apakah Slither berhasil, kalau tidak, lempar error
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # output JSON dari Slither
        slither_output = json.loads(result.stdout)

        # ubah sesuai kebutuhan
        formatted_issues = format_slither_output(slither_output)

        return AnalysisResponse(issues=formatted_issues)
    
    except subprocess.CalledProcessError as e:
        # jika Slither gagal dan harus lempar error
        raise HTTPException(status_code=400, detail=f"Slither analysis failed. The contract might have compilation errors. Error: {e.stderr}")
    
    except json.JSONDecodeError:
        # kalau output Slither tidak valid JSON
        raise HTTPException(status_code=500, detail="Failed to parse Slither's output. Please check the Slither installation and the contract code.")
    
    finally:
        # hapus tmp file
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)