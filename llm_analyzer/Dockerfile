# Base image
FROM python:3.10-slim

# working directory
WORKDIR /app

# caching layer docker
COPY requirements_llm.txt .

# dependencies Python
RUN pip install --no-cache-dir -r requirements_llm.txt

# sisa kode
COPY analysis_service_02.py .

# port yang digunakan
EXPOSE 8001

CMD ["uvicorn", "main_llm:app", "--host", "0.0.0.0", "--port", "8001"]
