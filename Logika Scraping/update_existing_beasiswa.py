import os
import sys
import json
import sqlite3

# Tambahkan path agar modul normalizer bisa di-import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from normalizer import normalize_beasiswa, clean_full_text, extract_lokasi, extract_tipe_beasiswa

def update_database():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'beaply.db')
    if not os.path.exists(db_path):
        print(f"Database tidak ditemukan di {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, nama, data_json FROM beasiswa")
    rows = cursor.fetchall()
    
    print(f"Mulai memperbarui {len(rows)} beasiswa di database...")
    updated_count = 0

    for row in rows:
        db_id = row['id']
        nama_db = row['nama']
        data_json_str = row['data_json']

        if not data_json_str:
            continue

        try:
            raw_data = json.loads(data_json_str)
            
            # Bersihkan full_text terlebih dahulu
            if 'full_text' in raw_data:
                raw_data['full_text'] = clean_full_text(raw_data['full_text'])
            if 'excerpt' in raw_data:
                raw_data['excerpt'] = clean_full_text(raw_data['excerpt'])

            # Kosongkan lokasi/tipe agar diekstrak ulang oleh normalizer dengan teks bersih
            raw_data['lokasi'] = ''
            raw_data['tipe_beasiswa'] = ''

            # Jalankan normalisasi
            norm = normalize_beasiswa(raw_data)

            # Klasifikasi kategori ulang sesuai logika database_beasiswa.py
            lokasi_val = str(norm.get('lokasi', '')).strip()
            penyelenggara_val = str(norm.get('penyelenggara', '')).strip() or "Tidak diketahui"
            
            if "luar negeri" in lokasi_val.lower() or lokasi_val == "Luar Negeri":
                kategori_val = "internasional"
            elif any(k in penyelenggara_val.lower() for k in ["pemerintah", "kementerian", "kemendikbud", "baznas", "dinas", "pemprov", "pemkot", "pemkab"]):
                kategori_val = "pemerintah"
            else:
                kategori_val = "swasta"

            # Perbarui data_json yang disimpan agar bersih
            new_data_json = json.dumps(norm)

            # Update ke database
            cursor.execute("""
                UPDATE beasiswa
                SET lokasi = ?,
                    tipe_beasiswa = ?,
                    kategori = ?,
                    data_json = ?
                WHERE id = ?
            """, (
                lokasi_val if lokasi_val else None,
                norm.get('tipe_beasiswa') if norm.get('tipe_beasiswa') else None,
                kategori_val,
                new_data_json,
                db_id
            ))
            updated_count += 1

            if "amartha" in nama_db.lower():
                print(f"-> [UPDATE] {nama_db[:50]}... | Lokasi Baru: {lokasi_val or 'Dalam Negeri'} | Kategori Baru: {kategori_val}")

        except Exception as e:
            print(f"Gagal memproses ID {db_id}: {e}")

    conn.commit()
    conn.close()
    print(f"Pembaruan selesai. {updated_count} beasiswa berhasil diperbarui.")

if __name__ == '__main__':
    update_database()
