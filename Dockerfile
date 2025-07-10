#Dockerfile
# ==============================================================================

# Gunakan base image Python official (slim biar ringan)
FROM python:3.11-slim

# Install dependencies OS penting: Tesseract OCR, Poppler (buat convert PDF), dan lib yang dibutuhin OpenCV
# Pisahkan installasi build-dependencies dan runtime-dependencies
# Gunakan --no-install-recommends untuk menghindari instalasi paket yang tidak wajib
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-ind \
    poppler-utils \
    libsm6 \
    libxext6 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install build dependencies yang hanya dibutuhkan saat kompilasi
# Contoh: jika ada library python yang butuh kompilasi C/C++ seperti numpy/opencv-python
# Setelah pip install, build dependencies ini akan dihapus
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory di container
WORKDIR /app

# Copy requirements.txt dulu (buat cache layer)
COPY requirements.txt .

# Copy .env file
COPY .env .env

# Install Python dependencies dan hapus build dependencies setelahnya
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc libxrender-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy seluruh source code ke container
COPY . .

# Expose port Flask default
EXPOSE 5000

# Jalankan app (sesuaikan dengan nama file utama lo, misal app.py)
CMD ["python","-m", "app.app"]