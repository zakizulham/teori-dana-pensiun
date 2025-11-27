"""
Kalkulator Anuitas Hidup Temporer (ä_x:n|).

Skrip ini menghitung faktor anuitas hidup temporer yang digunakan untuk
menghitung Nilai Sekarang dari Iuran Normal dalam metode seperti
Projected Unit Credit (PUC).
"""

import pandas as pd
import numpy_financial as npf

# ==============================================================================
# ASUMSI UTAMA - HARAP DISESUAIKAN DENGAN PROYEK BARU ANDA
# ==============================================================================

# Pilih asumsi bunga aktuaria Anda dari slide (misal 8.5% atau 7%)
TINGKAT_BUNGA_AKTUARIA = 0.07 

USIA_AWAL = 28
USIA_PENSIUN = 65
MASA_KERJA = USIA_PENSIUN - USIA_AWAL  # 28 tahun

# ==============================================================================
# FUNGSI PERHITUNGAN
# ==============================================================================

def hitung_faktor_anuitas_temporer(usia, durasi, tabel_mortalita_df, imbal_hasil):
    """
    Menghitung faktor anuitas hidup temporer (ä_x:n|).
    
    Args:
        usia (int): Usia awal (x)
        durasi (int): Lamanya periode (n)
        tabel_mortalita_df (pd.DataFrame): DataFrame tabel mortalita (harus ada 'lx')
        imbal_hasil (float): Tingkat bunga/diskonto per periode
    """
    
    try:
        # Ambil 'lx' pada usia awal sebagai basis (l_x)
        lx_awal = tabel_mortalita_df.loc[usia, 'lx']
    except KeyError:
        print(f"ERROR: Usia {usia} tidak ditemukan di indeks tabel.")
        return None
        
    faktor_anuitas = 0
    
    # Looping hanya selama 'durasi' (n) tahun, bukan sampai akhir tabel
    # Rumus: SUM [ (v^t) * (l_{x+t} / l_x) ] untuk t dari 0 s.d. n-1
    for t in range(durasi):
        usia_t = usia + t
        if usia_t in tabel_mortalita_df.index:
            lx_t = tabel_mortalita_df.loc[usia_t, 'lx']
            
            # Probabilitas hidup (t_px) = l_{x+t} / l_x
            prob_bertahan_hidup = lx_t / lx_awal 
            
            # Faktor diskonto (v^t) = 1 / (1 + i)^t
            faktor_diskonto = (1 / (1 + imbal_hasil))**t
            
            # Jumlahkan Present Value dari probabilitas pembayaran
            faktor_anuitas += prob_bertahan_hidup * faktor_diskonto
        else:
            # Berhenti jika usia t sudah di luar tabel mortalita
            print(f"Peringatan: Perhitungan berhenti di t={t} karena usia {usia_t} di luar tabel.")
            break
            
    return faktor_anuitas

def hitung_anuitas_dari_file(gender_char, usia, durasi, rate):
    """Fungsi helper untuk memuat file dan menjalankan perhitungan."""
    nama_file = f'data/tmi_4_{gender_char}.csv'
    try:
        # Muat tabel mortalita dari file CSV yang sudah Anda miliki
        tabel_mortalita = pd.read_csv(nama_file)
        tabel_mortalita.set_index('usia', inplace=True)
        
        # Panggil fungsi perhitungan
        hasil = hitung_faktor_anuitas_temporer(usia, durasi, tabel_mortalita, rate)
        
        if hasil is not None:
            notasi = f"ä_{usia}:{durasi}|"
            print(f"✅ Hasil untuk: {nama_file} (TMI 4 {gender_char.upper()})")
            print(f"   -> Faktor Anuitas {notasi} @ {rate*100:.2f}% = {hasil:.4f}")
        
    except FileNotFoundError:
        print(f"❌ GAGAL: File {nama_file} tidak ditemukan.")
        print("   Pastikan skrip ini ada di folder yang sama dengan 'kalkulator2.py'")
    except KeyError as e:
        print(f"❌ GAGAL: Kolom CSV tidak sesuai. Pastikan ada kolom 'usia' dan 'lx'. Error: {e}")
    except Exception as e:
        print(f"❌ GAGAL: Terjadi error. {e}")

# ==============================================================================
# EKSEKUSI UTAMA
# ==============================================================================
if __name__ == "__main__":
    print("--- Menghitung Faktor Anuitas Hidup Temporer (ä_x:n|) ---")
    print(f"Asumsi Tingkat Bunga: {TINGKAT_BUNGA_AKTUARIA*100:.2f}% p.a.")
    print(f"Periode: {MASA_KERJA} tahun, mulai dari usia {USIA_AWAL}\n")
    
    # Hitung untuk Male
    hitung_anuitas_dari_file('m', USIA_AWAL, MASA_KERJA, TINGKAT_BUNGA_AKTUARIA)
    
    print("-" * 20)
    
    # Hitung untuk Female
    hitung_anuitas_dari_file('f', USIA_AWAL, MASA_KERJA, TINGKAT_BUNGA_AKTUARIA)