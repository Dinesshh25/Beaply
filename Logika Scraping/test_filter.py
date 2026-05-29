"""
test_filter.py
Tes cepat untuk memverifikasi logika filter is_mahasiswa_only().
"""

from normalizer import extract_jenjang, is_mahasiswa_only

# ── Data contoh beasiswa ─────────────────────────────────────────
test_cases = [
    # (nama, jenjang_list, expected_result)
    ("Beasiswa S1 Unggulan Kemendikbud",           ["S1"],           True),
    ("Beasiswa Magister LPDP",                     ["S2"],           True),
    ("Beasiswa Doktoral Fulbright",                ["S3"],           True),
    ("Beasiswa D3 Vokasi",                         ["D3"],           True),
    ("Beasiswa D4 Sarjana Terapan",                ["D4"],           True),
    ("Beasiswa S1 dan S2 Djarum",                  ["S1", "S2"],     True),
    ("Beasiswa S1 SMA SMK Sederajat",              ["S1", "SMA"],    True),   # campuran → lolos (ada S1)
    ("Beasiswa SMA Berprestasi",                   ["SMA"],          False),  # khusus SMA → DITOLAK
    ("Beasiswa SMK Juara",                         ["SMA"],          False),  # SMK masuk kategori SMA → DITOLAK
    ("Beasiswa Tanpa Info Jenjang",                [],               True),   # tidak ada info → lolos
]

print("=" * 70)
print("  🧪 TES LOGIKA FILTER is_mahasiswa_only()")
print("=" * 70)

passed = 0
failed = 0

for nama, jenjang, expected in test_cases:
    result = is_mahasiswa_only(jenjang)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    if result == expected:
        passed += 1
    else:
        failed += 1

    print(f"\n  {status}")
    print(f"    Nama    : {nama}")
    print(f"    Jenjang : {jenjang}")
    print(f"    Hasil   : {'Lolos (mahasiswa)' if result else 'DITOLAK (SMA/SMK)'}")
    print(f"    Expected: {'Lolos' if expected else 'DITOLAK'}")

# ── Tes dari teks (tanpa jenjang eksplisit) ──────────────────────
print("\n" + "=" * 70)
print("  🧪 TES DETEKSI JENJANG DARI TEKS")
print("=" * 70)

text_cases = [
    ("Beasiswa untuk siswa SMA/SMK berprestasi se-Indonesia",     False),
    ("Program beasiswa S1 untuk mahasiswa teknik informatika",     True),
    ("Beasiswa kuliah S2 di Jepang untuk lulusan sarjana",        True),
    ("Bantuan pendidikan bagi pelajar SMA sederajat",             False),
    ("Beasiswa pendidikan tinggi dalam negeri",                   True),   # tidak ada jenjang → lolos
]

for teks, expected in text_cases:
    jenjang_detected = extract_jenjang(teks)
    result = is_mahasiswa_only(jenjang_detected, teks)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    if result == expected:
        passed += 1
    else:
        failed += 1

    print(f"\n  {status}")
    print(f"    Teks    : {teks}")
    print(f"    Jenjang : {jenjang_detected}")
    print(f"    Hasil   : {'Lolos (mahasiswa)' if result else 'DITOLAK (SMA/SMK)'}")
    print(f"    Expected: {'Lolos' if expected else 'DITOLAK'}")

# ── Ringkasan ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print(f"  📊 HASIL: {passed} PASSED, {failed} FAILED dari {passed + failed} test cases")
print("=" * 70 + "\n")
