## app/ocr/processor.py
# -*- coding: utf-8 -*-
# This file is part of the Tesseract OCR Invoice Processor project.

import os
import traceback
import cv2
import numpy as np
import pytesseract
from flask import jsonify
from pdf2image import convert_from_path
from PIL import Image
from extractor import (
    extract_faktur_tanggal, extract_jenis_pajak,
    extract_npwp_nama_rekanan, extract_dpp,
    extract_ppn, extract_keterangan
)
from utils.file_utils import allowed_file, simpan_preview_image

def preprocess_for_ocr(img):
    """Convert BGR → Grayscale + Adaptive Threshold (binarization)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    return thresh

def process_invoice_file(request, config):
    if "file" not in request.files:
        return jsonify(error="File tidak ditemukan"), 400

    file = request.files["file"]
    nama_pt_utama = request.form.get("nama_pt_utama", "").strip()

    if not nama_pt_utama:
        return jsonify(error="Nama PT Utama wajib diisi"), 400

    if not allowed_file(file.filename):
        return jsonify(error="File tidak didukung. Gunakan PDF atau gambar"), 400

    filepath = os.path.join(config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    try:
        if file.filename.lower().endswith(".pdf"):
            images = convert_from_path(filepath) # poppler_path sudah dihapus, sangat baik!
        else:
            with Image.open(filepath) as img:
                images = [img.copy()]  # salinan aman

        hasil_semua_halaman = []

        for i, image in enumerate(images):
            halaman_ke = i + 1
            print(f"\n=== [📝 DEBUG] MEMPROSES HALAMAN {halaman_ke} ===")

            if isinstance(image, np.ndarray):
                img_cv = image
            else:
                img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            thresh = preprocess_for_ocr(img_cv)

            preview_filename = simpan_preview_image(
                pil_image=image,
                upload_folder=config['UPLOAD_FOLDER'],
                page_num=halaman_ke,
                original_filename=file.filename
            )

            raw_text = pytesseract.image_to_string(img_cv, lang="ind", config="--psm 6")
            no_faktur, tanggal_obj = extract_faktur_tanggal(raw_text)

            jenis_pajak, blok_rekanan, _ = extract_jenis_pajak(raw_text, nama_pt_utama)
            if not jenis_pajak:
                hasil_semua_halaman.append(
                    {"error": f"Hal {halaman_ke}: Nama PT Utama tidak ditemukan."}
                )
                continue

            nama_rekanan, npwp_rekanan = extract_npwp_nama_rekanan(blok_rekanan)
            if not no_faktur:
                hasil_semua_halaman.append(
                    {"error": f"Hal {halaman_ke}: Tidak ditemukan tanggal/faktur"}
                )
                continue

            dpp, dpp_str, override_ppn, override_ppn_str = extract_dpp(raw_text)
            ppn, ppn_str = extract_ppn(raw_text, dpp, override_ppn)
            keterangan = extract_keterangan(raw_text)

            hasil_halaman = {
                "klasifikasi": jenis_pajak,
                "data": {
                    # GUNAKAN KONDISI INI: Jika tanggal_obj ada, format. Jika tidak, beri string kosong.
                    "bulan": tanggal_obj.strftime("%B") if tanggal_obj else "",
                    "tanggal": tanggal_obj.strftime("%Y-%m-%d") if tanggal_obj else "",
                    "keterangan": keterangan,
                    "npwp_lawan_transaksi": npwp_rekanan,
                    "nama_lawan_transaksi": nama_rekanan,
                    "no_faktur": no_faktur,
                    "dpp": dpp,
                    "dpp_str": dpp_str,
                    "ppn": ppn,
                    "ppn_str": ppn_str,
                    "formatted_dpp": dpp_str,
                    "formatted_ppn": ppn_str,
                    "halaman": halaman_ke,
                    "preview_image": preview_filename,
                    "raw_ocr": raw_text,
                },
            }

            if not tanggal_obj:
                hasil_halaman["warning_message"] = (
                    "Tanggal tidak terdeteksi, mohon isi manual."
                )

            hasil_semua_halaman.append(hasil_halaman)

        return (
            jsonify(
                {
                    "success": True,
                    "results": hasil_semua_halaman,
                    "total_halaman": len(images),
                }
            ),
            200,
        )

    except Exception as err:
        print(f"[❌ ERROR] {traceback.format_exc()}")
        return jsonify(error=traceback.format_exc()), 500

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)