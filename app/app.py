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

# Inisialisasi database
with app.app_context():
    db.create_all()

# ==============================================================================  
# ROUTES  
# ==============================================================================

@app.route("/")
def index():
    return "Hello from Tesseract OCR container!"

@app.route("/api/process", methods=["POST"])
def process_file():
    return process_invoice_file(request, app.config)

@app.route("/api/save", methods=["POST"])
def save_data():
    if not request.is_json:
        return jsonify(error="Request harus berupa JSON."), 400

    data = request.get_json()

    try:
        if isinstance(data, list):
            for item in data:
                save_invoice_data(item, db)  # Pastikan fungsi ini di-import
            db.session.commit()
            return jsonify(message=f"{len(data)} faktur berhasil disimpan."), 201
        else:
            save_invoice_data(data, db)
            db.session.commit()
            return jsonify(message="Faktur berhasil disimpan."), 201

    except ValueError as ve:
        db.session.rollback()
        return jsonify(error=str(ve)), 400

    except Exception as e:
        db.session.rollback()
        print(f"[❌ ERROR /api/save] {e}")
        return jsonify(error=f"Terjadi kesalahan di server: {e}"), 500

# Optional routes — uncomment kalau udah siap
# @app.route("/api/export", methods=["GET"])
# def export_excel():
#     return generate_excel_export(db)

# @app.route("/api/history", methods=["GET"])
# def route_get_history():
#     return get_history()

# @app.route("/api/delete/<string:jenis>/<int:id>", methods=["DELETE"])
# def route_delete_faktur(jenis, id):
#     return delete_faktur(jenis, id)

@app.route("/preview/<filename>")
def serve_preview(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, mimetype="image/jpeg")

# ==============================================================================  
# Entry Point Saat Dipanggil dari Docker  
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Running Flask on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
