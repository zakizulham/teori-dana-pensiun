"""
Kalkulator Iuran DPLK untuk Target Income Replacement Ratio (IRR).

Skrip ini menghitung iuran bulanan yang diperlukan untuk program pensiun DPLK
guna mencapai target IRR tertentu, dengan memperhitungkan manfaat yang sudah ada
dari JHT dan Uang Pesangon (UUCK).
"""

import pandas as pd
import numpy_financial as npf

# ==============================================================================
# TAHAP 1: INISIALISASI & ASUMSI
# ==============================================================================
# Definisikan semua asumsi dari studi kasus ke dalam variabel.

# --- Asumsi Individu ---
gender = 'm'  # 'm' untuk male, 'f' untuk female
usia_awal = 40  # tahun
usia_pensiun = 55  # tahun
gaji_awal_bulanan = 8_000_000  # Rp

# --- Asumsi Ekonomi & Pasar ---
kenaikan_gaji_pa = 0.05  # 5% per tahun
imbal_hasil_investasi_pa = 0.06  # 6% per tahun
target_irr = 0.80  # 80%

# --- Asumsi Program Pensiun ---
iuran_jht_total = 0.057  # 5.7% (3.7% Perusahaan + 2% Pekerja)
# Catatan: Manfaat Jaminan Pensiun (JP) diabaikan untuk saat ini karena
# pembayarannya dimulai pada usia 60, sedangkan target pensiun kita adalah 55.

# --- Variabel Perhitungan Turunan ---
masa_kerja = usia_pensiun - usia_awal  # dalam tahun
imbal_hasil_bulanan = (1 + imbal_hasil_investasi_pa)**(1 / 12) - 1


# ==============================================================================
# TAHAP 2: MEMUAT DATA MORTALITA
# ==============================================================================
try:
    nama_file_mortalita = f'data/tmi_4_{gender}.csv'
    tabel_mortalita = pd.read_csv(nama_file_mortalita)
    # Set 'usia' sebagai index untuk mempermudah pencarian data
    tabel_mortalita.set_index('usia', inplace=True)
    print(f"✅ Berhasil memuat tabel mortalita: {nama_file_mortalita}")
except FileNotFoundError:
    print(f"❌ GAGAL: File {nama_file_mortalita} tidak ditemukan.")
    exit()
except KeyError:
    print(f"❌ GAGAL: Kolom 'usia' tidak ditemukan di {nama_file_mortalita}.")
    exit()


# ==============================================================================
# TAHAP 3: FUNGSI-FUNGSI PERHITUNGAN
# ==============================================================================

def hitung_gaji_akhir(gaji_awal, kenaikan_pa, tahun):
    """Menghitung proyeksi gaji di akhir masa kerja."""
    return npf.fv(kenaikan_pa, tahun, 0, -gaji_awal)


def hitung_akumulasi_jht(gaji_awal, kenaikan_gaji, imbal_hasil, masa_kerja_thn, iuran_rate):
    """Menghitung total dana JHT dengan metode iterasi per tahun."""
    saldo_jht = 0
    gaji_tahunan_saat_ini = gaji_awal * 12

    for _ in range(masa_kerja_thn):
        # Akumulasikan saldo dari tahun sebelumnya dengan imbal hasil
        saldo_jht = saldo_jht * (1 + imbal_hasil)

        # Hitung iuran tahun ini dan tambahkan ke saldo
        iuran_tahunan = gaji_tahunan_saat_ini * iuran_rate
        saldo_jht += iuran_tahunan

        # Naikkan gaji untuk perhitungan tahun depan
        gaji_tahunan_saat_ini *= (1 + kenaikan_gaji)

    return saldo_jht


def hitung_pesangon_uuck(gaji_akhir_bulanan, masa_kerja_tahun):
    """
    Menghitung pesangon berdasarkan aturan UUCK (disederhanakan).
    Masa kerja 15 tahun diasumsikan mendapat 9x gaji.
    """
    if masa_kerja_tahun >= 15:
        faktor_pengali = 9
    else:
        # Logika lain bisa ditambahkan untuk masa kerja berbeda
        faktor_pengali = 0

    return faktor_pengali * gaji_akhir_bulanan


def hitung_faktor_anuitas(usia, tabel_mortalita_df, imbal_hasil):
    """Menghitung faktor anuitas hidup (ä_x)."""
    # PERBAIKAN: Menggunakan kolom 'lx' sesuai data CSV yang baru.
    lx_awal = tabel_mortalita_df.loc[usia, 'lx']
    faktor_anuitas = 0

    # Looping dari usia sekarang sampai akhir tabel mortalita
    for t in range(len(tabel_mortalita_df) - usia):
        usia_t = usia + t
        if usia_t in tabel_mortalita_df.index:
            # PERBAIKAN: Menggunakan kolom 'lx'.
            lx_t = tabel_mortalita_df.loc[usia_t, 'lx']
            prob_bertahan_hidup = lx_t / lx_awal  # t_px
            faktor_diskonto = (1 / (1 + imbal_hasil))**t  # v^t
            faktor_anuitas += prob_bertahan_hidup * faktor_diskonto

    return faktor_anuitas


# ==============================================================================
# TAHAP 4: EKSEKUSI PERHITUNGAN UTAMA
# ==============================================================================
if __name__ == "__main__":
    print("\n--- MULAI KALKULASI STUDI KASUS IRR ---")

    # 1. Hitung Gaji Akhir & Target Pensiun
    gaji_akhir_bulanan = hitung_gaji_akhir(
        gaji_awal_bulanan, kenaikan_gaji_pa, masa_kerja
    )
    target_pensiun_bulanan = gaji_akhir_bulanan * target_irr

    print(f"\n[1] Proyeksi & Target Pensiun (Usia {usia_pensiun})")
    print(f"    - Gaji terakhir per bulan : Rp {gaji_akhir_bulanan:,.0f}")
    print(f"    - Target pensiun per bulan: Rp {target_pensiun_bulanan:,.0f}")

    # 2. Hitung Manfaat yang Sudah Ada (JHT & Pesangon)
    akumulasi_jht = hitung_akumulasi_jht(
        gaji_awal_bulanan, kenaikan_gaji_pa, imbal_hasil_investasi_pa,
        masa_kerja, iuran_jht_total
    )
    pesangon = hitung_pesangon_uuck(gaji_akhir_bulanan, masa_kerja)
    total_dana_lump_sum = akumulasi_jht + pesangon

    print(f"\n[2] Estimasi Manfaat Pensiun di Usia {usia_pensiun} (Lump Sum)")
    print(f"    - Akumulasi Dana JHT      : Rp {akumulasi_jht:,.0f}")
    print(f"    - Uang Pesangon (UUCK)    : Rp {pesangon:,.0f}")
    print("    -------------------------------------------------- +")
    print(f"    - Total Dana Siap Pakai   : Rp {total_dana_lump_sum:,.0f}")

    # 3. Konversi Dana Lump Sum menjadi Manfaat Pensiun Bulanan
    faktor_anuitas_tahunan = hitung_faktor_anuitas(
        usia_pensiun, tabel_mortalita, imbal_hasil_investasi_pa
    )
    manfaat_pensiun_bulanan_existing = total_dana_lump_sum / (faktor_anuitas_tahunan * 12)

    print(f"\n[3] Konversi Dana ke Pensiun Bulanan Seumur Hidup")
    print(f"    - Faktor Anuitas (ä_{usia_pensiun}) : {faktor_anuitas_tahunan:.4f}")
    print(f"    - Estimasi Pensiun Bulanan: Rp {manfaat_pensiun_bulanan_existing:,.0f}")

    # 4. Hitung Kekurangan (Gap)
    gap_pensiun_bulanan = target_pensiun_bulanan - manfaat_pensiun_bulanan_existing

    print(f"\n[4] Kebutuhan & Kekurangan Pensiun")
    print(f"    - Target Pensiun Bulanan  : Rp {target_pensiun_bulanan:,.0f}")
    print(f"    - Manfaat yang Ada        : Rp {manfaat_pensiun_bulanan_existing:,.0f}")
    print("    -------------------------------------------------- -")

    if gap_pensiun_bulanan > 0:
        print(f"    - Kekurangan (GAP)        : Rp {gap_pensiun_bulanan:,.0f}")

        # 5. Hitung Kebutuhan Dana DPLK dan Iuran Bulanannya
        kebutuhan_dana_dplk_lump_sum = gap_pensiun_bulanan * faktor_anuitas_tahunan * 12

        iuran_dplk_bulanan = -npf.pmt(
            rate=imbal_hasil_bulanan,
            nper=masa_kerja * 12,
            pv=0,
            fv=kebutuhan_dana_dplk_lump_sum
        )

        print("\n[5] Solusi: Iuran DPLK")
        print(f"    - Dana DPLK harus terkumpul: Rp {kebutuhan_dana_dplk_lump_sum:,.0f}")
        print(f"    - Persentase dari gaji awal: {iuran_dplk_bulanan / gaji_awal_bulanan:.2%}")
        print("\n==============================================================================")
        print(f"✅ IURAN DPLK BULANAN YANG DIPERLUKAN: Rp {iuran_dplk_bulanan:,.0f}")
        print("==============================================================================")

    else:
        print("\n✅ SELAMAT! Target pensiun Anda sudah terpenuhi dari program yang ada.")