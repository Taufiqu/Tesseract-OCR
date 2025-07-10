import sys
import os

# Tambahkan folder 'app/' ke sys.path supaya import modul jalan
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app import app  # from app/app.py
