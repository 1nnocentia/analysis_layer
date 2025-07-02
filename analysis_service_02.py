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

