"""
Kalkulator Anuitas Hidup Temporer (ä_x:n|) - Tabel GAM 71

Skrip ini menghitung faktor anuitas hidup temporer menggunakan tabel
GAM 71 Male & Female, sesuai asumsi di Slide 15.
"""

import pandas as pd
import numpy_financial as npf

# ==============================================================================
# ASUMSI UTAMA - HARAP DISESUAIKAN DENGAN PROYEK BARU ANDA
# ==============================================================================

# Pilih asumsi bunga aktuaria Anda dari slide (misal 8.5% atau 7%)
TINGKAT_BUNGA_AKTUARIA = 0.07  # <-- GANTI INI! (Contoh: 8.5%)

USIA_AWAL = 28
USIA_PENSIUN = 56
MASA_KERJA = USIA_PENSIUN - USIA_AWAL  # 28 tahun

# ==============================================================================
# FUNGSI PERHITUNGAN (Logika ini sama persis seperti skrip TMI 4)
# ==============================================================================

def hitung_faktor_anuitas_temporer(usia, durasi, tabel_mortalita_df, imbal_hasil):
    """
    Menghitung faktor anuitas hidup temporer (ä_x:n|).
    """
    
    try:
        lx_awal = tabel_mortalita_df.loc[usia, 'lx']
    except KeyError:
        print(f"ERROR: Usia {usia} tidak ditemukan di indeks tabel.")
        return None
        
    faktor_anuitas = 0
    
    # Looping hanya selama 'durasi' (n) tahun
    for t in range(durasi):
        usia_t = usia + t
        if usia_t in tabel_mortalita_df.index:
            lx_t = tabel_mortalita_df.loc[usia_t, 'lx']
            prob_bertahan_hidup = lx_t / lx_awal 
            faktor_diskonto = (1 / (1 + imbal_hasil))**t
            faktor_anuitas += prob_bertahan_hidup * faktor_diskonto
        else:
            print(f"Peringatan: Perhitungan berhenti di t={t} karena usia {usia_t} di luar tabel.")
            break
            
    return faktor_anuitas

def hitung_anuitas_dari_file(gender_char, tabel_nama, usia, durasi, rate):
    """Fungsi helper yang dimodifikasi untuk memanggil file GAM 71."""
    
    # Mengarahkan langsung ke file GAM 71 di folder data Anda
    nama_file = f'data/{tabel_nama}_{gender_char}.csv' 
    
    try:
        tabel_mortalita = pd.read_csv(nama_file)
        tabel_mortalita.set_index('usia', inplace=True)
        
        # Panggil fungsi perhitungan
        hasil = hitung_faktor_anuitas_temporer(usia, durasi, tabel_mortalita, rate)
        
        if hasil is not None:
            notasi = f"ä_{usia}:{durasi}|"
            print(f"✅ Hasil untuk: {nama_file} ({tabel_nama.upper()} {gender_char.upper()})")
            print(f"   -> Faktor Anuitas {notasi} @ {rate*100:.2f}% = {hasil:.4f}")
        
    except FileNotFoundError:
        print(f"❌ GAGAL: File {nama_file} tidak ditemukan.")
    except KeyError as e:
        print(f"❌ GAGAL: Kolom CSV tidak sesuai. Pastikan ada 'usia' dan 'lx'. Error: {e}")
    except Exception as e:
        print(f"❌ GAGAL: Terjadi error. {e}")

# ==============================================================================
# EKSEKUSI UTAMA
# ==============================================================================
if __name__ == "__main__":
    print("--- Menghitung Faktor Anuitas (ä_x:n|) - Tabel GAM 71 ---")
    print(f"Asumsi Tingkat Bunga: {TINGKAT_BUNGA_AKTUARIA*100:.2f}% p.a.")
    print(f"Periode: {MASA_KERJA} tahun, mulai dari usia {USIA_AWAL}\n")
    
    # Hitung untuk Male
    hitung_anuitas_dari_file('m', 'gam_71', USIA_AWAL, MASA_KERJA, TINGKAT_BUNGA_AKTUARIA)
    
    print("-" * 20)
    
    # Hitung untuk Female
    hitung_anuitas_dari_file('f', 'gam_71', USIA_AWAL, MASA_KERJA, TINGKAT_BUNGA_AKTUARIA)