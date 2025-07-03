# Gunakan base image Python 3.9
FROM python:3.9-slim

# Tentukan direktori kerja
WORKDIR /app

# Instal hanya build-essential dari apt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Definisikan trusted hosts untuk pip
ARG PIP_TRUSTED_HOSTS="--trusted-host pypi.org --trusted-host files.pythonhosted.org"

# Update pip
RUN python -m pip install --upgrade pip ${PIP_TRUSTED_HOSTS}

# 1. Instal solc-select untuk manajemen versi Solidity
RUN pip install solc-select ${PIP_TRUSTED_HOSTS}

# 2. Instal dan gunakan versi solc yang spesifik (misalnya 0.8.20)
RUN solc-select install 0.8.28 && solc-select use 0.8.28

# 3. Tambahkan lokasi solc ke PATH agar bisa ditemukan oleh Slither
ENV PATH="/root/.solc-select/bin:$PATH"

# Instal Slither (sekarang dia akan menemukan solc)
RUN pip install slither-analyzer ${PIP_TRUSTED_HOSTS}

# Salin file requirements
COPY requirements.txt .

# Instal library dari requirements.txt
RUN pip install -r requirements.txt ${PIP_TRUSTED_HOSTS}

# Salin sisa kode aplikasi
COPY analysis_service_01_slither.py .

# Expose port
EXPOSE 8000

# Jalankan aplikasi
CMD ["uvicorn", "analysis_service_01_slither:app", "--host", "0.0.0.0", "--port", "8000"]