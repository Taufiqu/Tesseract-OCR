# app/run.py
import sys
import os

# Dapatkan direktori dari run.py
current_dir = os.path.dirname(os.path.abspath(__file__))

# Jalur ke direktori *yang mengandung* modul 'app' utama Anda.
# Berdasarkan struktur file yang Anda berikan:
# 'app' berada di dalam 'taufiqu/tesseract-ocr/Tesseract-OCR-5937d393c4e5bc8e718170f0ede709930bfe1108/'
app_parent_dir = os.path.join(current_dir, 'taufiqu', 'tesseract-ocr', 'Tesseract-OCR-5937d393c4e5bc8e718170f0ede709930bfe1108')

# Tambahkan direktori ini ke sys.path
sys.path.insert(0, app_parent_dir)

# Sekarang, import ini seharusnya dapat menemukan app/app.py
from app import app