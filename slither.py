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
    """