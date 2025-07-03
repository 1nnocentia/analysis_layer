# tarik data pakai FastAPI

import uvicorn # server ASGI (Asynchronous Server Gateway Interface) -> menjalankan FastAPI secra lokal
import subprocess # untuk menjalankan slither dari python
import json # konversi antara py dan json
import tempfile # temporary file
import os # berinteraksi dengan path/env/file system
import logging
from fastapi import FastAPI, HTTPException # untuk buat endpoint
from pydantic import BaseModel # class model untuk validasi data (JSON request)
from typing import List # variable type untuk list

# buat logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

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
    version="2.1.0"
)

# 3. Helper untuk transformasi output

def format_slither_output(slither_row_json: dict) -> List[Issue]:
    """
    Mengubah output JSON dari Slither menjadi format sesuai dengan input di layer setelahnya
    """
    formated_issues = []

    # validasi apakah analisis berhasil
    if not slither_row_json.get("results", {}).get('detectors'):
        return []
    
    detectors = slither_row_json["results"]["detectors"]

    for detector in detectors:
        # informasi dasar
        issue_type = detector.get("check", "N/A")
        severity = detector.get("impact", "N/A")
        # ambil infromasi dari Slither
        message = detector.get("description", "No description available").split("\n")[0]

        # detektor bisa punya beberapa lokasi
        if "elements" in detector:
            for element in detector["elements"]:
                # ambil nomor baris dari elemen
                line_number = element.get("source_mapping", {}).get("line", [0])[0]
                
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
        slither_executable_path = "/usr/local/bin/slither"
        command = [slither_executable_path, tmp_file_path, "--json", "-"]

        # eksekusi command
        # cek apakah Slither berhasil, kalau tidak, lempar error
        result = subprocess.run(command, capture_output=True, text=True) #, check=True
        logger.info(f"Command finished with return code: {result.returncode}")

        try:
            slither_output = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.error("Crashed, Slither not produced valid JSON output.")
            logger.debug(f"Slither STDERR: {result.stderr}")
            raise HTTPException(status_code=500, detail="Failed to parse Slither's output. Please check the Slither installation and the contract code.")

        if slither_output.get("success"):
            logger.info("Slither analysis completed successfully.")
            formatted_issues = format_slither_output(slither_output)
            return AnalysisResponse(issues=formatted_issues)
        else:
            error_message = slither_output.get("error", "Unknown error")
            logger.warning(f"Slither analysis failed with error: {error_message}")
            raise HTTPException(status_code=400, detail=f"Slither analysis failed: {error_message}")
        
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during Slither analysis. {type(e).__name__} - {e}")
    
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

# 5. Run lahhh
# uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)