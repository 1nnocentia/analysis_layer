# Gunakan base image Python 3.9
FROM python:3.9-slim

# Tentukan direktori kerja
WORKDIR /app

# Definisikan trusted hosts untuk konsistensi
ARG PIP_TRUSTED_HOSTS="--trusted-host pypi.org --trusted-host files.pythonhosted.org"

# Salin dan instal requirements
COPY requirements.txt .
RUN pip install -r requirements.txt ${PIP_TRUSTED_HOSTS}

# Salin kode aplikasi
COPY analysis_service_02.py .

# Expose port
EXPOSE 8001

# PERBAIKAN DI SINI: Gunakan "analysis_service_02:app" bukan "main_llm:app"
CMD ["uvicorn", "analysis_service_02:app", "--host", "0.0.0.0", "--port", "8001"]