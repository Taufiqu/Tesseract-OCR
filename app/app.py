# ==============================================================================  
# File: app/app.py  
# Deskripsi: Entry point utama Flask, langsung bisa dijalankan dari Docker  
# ==============================================================================

# 1. Pustaka Standar
import os

# 2. Pustaka Pihak Ketiga
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 3. Impor Lokal
from app.config import Config
from app.ocr.processor import process_invoice_file
# from app.db.saver import save_invoice_data  # Uncomment kalo udah ada
# from app.exporter.export_excel import generate_excel_export
# from app.history.reader import get_history
# from app.db.deleter import delete_faktur

# ==============================================================================  
# Inisialisasi Flask App  
# ==============================================================================

print("📦 DATABASE_URL =", os.getenv("DATABASE_URL"))
print("🌐 FRONTEND_URL =", os.getenv("FRONTEND_URL"))
print("📁 UPLOAD_FOLDER =", os.getenv("UPLOAD_FOLDER"))

app = Flask(__name__)
app.config.from_object(Config)

# CORS
CORS(app, origins=[
    "http://localhost:3000",
    "https://proyek-pajak.vercel.app",
    os.environ.get("FRONTEND_URL")
], supports_credentials=True)

# Database & Migrasi
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# ==============================================================================  
# ROUTES  
# ==============================================================================

@app.route("/")
def index():
    return "Hello from Tesseract OCR container!"

@app.route("/api/process", methods=["POST"])
def process_file():
    print("🚀 Route /api/process terpanggil")
    return process_invoice_file(request, app.config)

@app.route("/preview/<filename>")
def serve_preview(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, mimetype="image/jpeg")

# ==============================================================================  
# Entry Point Saat Dipanggil dari Docker  
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Running Flask on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
