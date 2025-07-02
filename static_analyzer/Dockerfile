# base image
FROM python:3.10-slim

# working directory
WORKDIR /app

# instal git dan library
RUN apt-get update && apt-get install -y git build-essential

# manajemen versi solidity
RUN pip install solc-select

# atur versi
RUN solc-select install 0.8.20 && solc-select use 0.8.20

# caching layer docker
COPY requirements.txt .

# dependencies python
RUN pip install --no-cache-dir -r requirements.txt

# sisa kodenya
COPY analysis_service_01_slither.py .

# port yang digunakan
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]