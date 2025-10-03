"""
Kalkulator Iuran DPLK untuk Target Income Replacement Ratio (IRR).

Versi 2.0: Perhitungan ini sudah memasukkan pertimbangan manfaat dari
Jaminan Pensiun (JP) BPJS Ketenagakerjaan, yang membuat estimasi lebih akurat.

Skrip ini menghitung iuran bulanan DPLK yang diperlukan untuk mencapai target
IRR dengan memperhitungkan manfaat dari JHT, Uang Pesangon (UUCK), dan JP.
"""

import pandas as pd
import numpy_financial as npf

# ==============================================================================
# TAHAP 1: INISIALISASI & ASUMSI
# ==============================================================================
# --- Asumsi Individu ---
gender = 'm'  # 'm' untuk male, 'f' untuk female
usia_awal = 40  # tahun
usia_pensiun = 55  # tahun
gaji_awal_bulanan = 8_000_000  # Rp

# --- Asumsi Ekonomi & Pasar ---
kenaikan_gaji_pa = 0.05  # 5% per tahun
imbal_hasil_investasi_pa = 0.06  # 6% per tahun
target_irr = 0.80  # 80%

# --- Asumsi Program Pensiun Wajib ---
iuran_jht_total = 0.057  # 5.7% (Perusahaan + Pekerja)

# --- ASUMSI BARU: JAMINAN PENSIUN (JP) ---
usia_pensiun_jp = 60  # Manfaat JP cair di usia 60 tahun
usia_mulai_iuran_jp = 25  # Asumsi mulai menjadi peserta JP di usia 25
batas_atas_manfaat_jp = 4_792_300  # Batas atas manfaat JP bulanan

# --- Variabel Perhitungan Turunan ---
masa_kerja = usia_pensiun - usia_awal  # dalam tahun
imbal_hasil_bulanan = (1 + imbal_hasil_investasi_pa)**(1 / 12) - 1


# ==============================================================================
# TAHAP 2: MEMUAT DATA MORTALITA
# ==============================================================================
try:
    nama_file_mortalita = f'data/tmi_4_{gender}.csv'
    tabel_mortalita = pd.read_csv(nama_file_mortalita)
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
        saldo_jht = saldo_jht * (1 + imbal_hasil)
        iuran_tahunan = gaji_tahunan_saat_ini * iuran_rate
        saldo_jht += iuran_tahunan
        gaji_tahunan_saat_ini *= (1 + kenaikan_gaji)
    return saldo_jht


def hitung_pesangon_uuck(gaji_akhir_bulanan, masa_kerja_tahun):
    """Menghitung pesangon UUCK (disederhanakan)."""
    if masa_kerja_tahun >= 15:
        faktor_pengali = 9
    else:
        faktor_pengali = 0
    return faktor_pengali * gaji_akhir_bulanan


def hitung_faktor_anuitas(usia, tabel_mortalita_df, imbal_hasil):
    """Menghitung faktor anuitas hidup (ä_x)."""
    lx_awal = tabel_mortalita_df.loc[usia, 'lx']
    faktor_anuitas = 0
    for t in range(len(tabel_mortalita_df) - usia):
        usia_t = usia + t
        if usia_t in tabel_mortalita_df.index:
            lx_t = tabel_mortalita_df.loc[usia_t, 'lx']
            prob_bertahan_hidup = lx_t / lx_awal
            faktor_diskonto = (1 / (1 + imbal_hasil))**t
            faktor_anuitas += prob_bertahan_hidup * faktor_diskonto
    return faktor_anuitas


def hitung_pv_manfaat_jp(gaji_akhir_bln, tabel_mortalita_df):
    """
    Menghitung Present Value (PV) dari manfaat JP di usia 55.
    Logika disesuaikan agar identik dengan model Excel.
    """
    # 1. Estimasi manfaat JP bulanan di usia 60 (logika disederhanakan)
    masa_iuran_bulan = (usia_pensiun_jp - usia_mulai_iuran_jp) * 12
    
    manfaat_bulanan_raw = 0.01 * masa_iuran_bulan * gaji_akhir_bln
    
    manfaat_jp_bulanan = min(manfaat_bulanan_raw, batas_atas_manfaat_jp)

    # 2. Hitung nilai lump sum manfaat JP di usia 60 (logika tetap sama)
    faktor_anuitas_60 = hitung_faktor_anuitas(
        usia_pensiun_jp, tabel_mortalita_df, imbal_hasil_investasi_pa
    )
    nilai_lump_sum_di_60 = manfaat_jp_bulanan * 12 * faktor_anuitas_60

    # 3. Diskonto nilai tersebut ke usia 55 (logika tetap sama)
    periode_diskonto = usia_pensiun_jp - usia_pensiun
    pv_manfaat_jp_di_55 = nilai_lump_sum_di_60 / (1 + imbal_hasil_investasi_pa)**periode_diskonto
    
    # Kembalikan hasil perhitungan untuk digunakan
    return pv_manfaat_jp_di_55, manfaat_jp_bulanan, faktor_anuitas_60


# ==============================================================================
# TAHAP 4: EKSEKUSI PERHITUNGAN UTAMA
# ==============================================================================
if __name__ == "__main__":
    print("\n--- KALKULATOR PENSIUN V2 (TERMASUK JAMINAN PENSIUN) ---")

    # 1. Hitung Gaji Akhir & Target Pensiun (Sama seperti sebelumnya)
    gaji_akhir_bulanan = hitung_gaji_akhir(
        gaji_awal_bulanan, kenaikan_gaji_pa, masa_kerja
    )
    target_pensiun_bulanan = gaji_akhir_bulanan * target_irr
    print(f"\n[1] Proyeksi & Target Pensiun (Usia {usia_pensiun})")
    print(f"    - Gaji terakhir per bulan : Rp {gaji_akhir_bulanan:,.0f}")
    print(f"    - Target pensiun per bulan: Rp {target_pensiun_bulanan:,.0f}")

    # 2. Hitung Manfaat yang Ada (JHT, Pesangon, DAN JP)
    akumulasi_jht = hitung_akumulasi_jht(
        gaji_awal_bulanan, kenaikan_gaji_pa, imbal_hasil_investasi_pa,
        masa_kerja, iuran_jht_total
    )
    pesangon = hitung_pesangon_uuck(gaji_akhir_bulanan, masa_kerja)
    
    # PEMBARUAN: Panggil fungsi baru untuk menghitung PV dari JP
    pv_jp, est_manfaat_jp_bln, fa_60 = hitung_pv_manfaat_jp(gaji_akhir_bulanan, tabel_mortalita)
    
    total_dana_lump_sum = akumulasi_jht + pesangon + pv_jp

    print(f"\n[2] Estimasi Manfaat Pensiun di Usia {usia_pensiun} (Lump Sum Equivalent)")
    print(f"    - Akumulasi Dana JHT      : Rp {akumulasi_jht:,.0f}")
    print(f"    - Uang Pesangon (UUCK)    : Rp {pesangon:,.0f}")
    print(f"    - PV Manfaat JP di Usia 55: Rp {pv_jp:,.0f}")
    print("    -------------------------------------------------- +")
    print(f"    - Total Dana Siap Pakai   : Rp {total_dana_lump_sum:,.0f}")
    
    # 3. Konversi Dana Lump Sum menjadi Manfaat Pensiun Bulanan
    faktor_anuitas_55 = hitung_faktor_anuitas(
        usia_pensiun, tabel_mortalita, imbal_hasil_investasi_pa
    )
    manfaat_pensiun_bulanan_existing = total_dana_lump_sum / (faktor_anuitas_55 * 12)
    
    print(f"\n[3] Konversi Dana ke Pensiun Bulanan Seumur Hidup")
    print(f"    - Faktor Anuitas (ä_{usia_pensiun}) : {faktor_anuitas_55:.4f}")
    print(f"    - Faktor Anuitas (ä_{usia_pensiun_jp}) : {fa_60:.4f}") # <-- TAMBAHAN BARIS INI
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
        kebutuhan_dana_dplk_lump_sum = gap_pensiun_bulanan * faktor_anuitas_55 * 12
        
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
        print(f"✅ IURAN DPLK BULANAN (DENGAN JP): Rp {iuran_dplk_bulanan:,.0f}")
        print("==============================================================================")
    else:
        print("\n✅ SELAMAT! Target pensiun Anda sudah terpenuhi dari program yang ada.")