import math

def dapatkan_input_integer(prompt):
    """Fungsi helper untuk meminta input ANGKA BULAT (menghapus titik/koma)."""
    while True:
        try:
            nilai_str = input(prompt)
            # Menghapus semua pemisah ribuan (titik dan koma)
            nilai_str_bersih = nilai_str.replace('.', '').replace(',', '')
            return int(nilai_str_bersih)
        except ValueError:
            print("Input tidak valid. Harap masukkan angka bulat saja (contoh: 9000000).")
        except Exception as e:
            print(f"Terjadi error: {e}")

def dapatkan_input_float(prompt):
    """Fungsi helper untuk meminta input ANGKA DESIMAL (hanya menghapus koma)."""
    while True:
        try:
            nilai_str = input(prompt)
            # Hanya menghapus koma, titik dianggap sebagai desimal
            nilai_str_bersih = nilai_str.replace(',', '')
            return float(nilai_str_bersih)
        except ValueError:
            print("Input tidak valid. Harap masukkan angka desimal (contoh: 12.2 atau 7461886987.66).")
        except Exception as e:
            print(f"Terjadi error: {e}")

def main():
    """
    Fungsi utama untuk menjalankan kalkulator IRR
    berdasarkan data dari spreadsheet Vertex42.
    """
    print("=" * 50)
    print("ANALISIS HASIL KALKULATOR PENSIUN (PPIP) - V2.1 (FINAL FIX)")
    print("=" * 50)
    print("Skrip ini akan melanjutkan perhitungan dari spreadsheet Anda.")
    print("Harap masukkan asumsi dan hasil dari file Excel:\n")

    # --- TAHAP 1: KUMPULKAN ASUMSI & HASIL ---
    
    # Asumsi Profil & Ekonomi
    gaji_awal_bulanan = dapatkan_input_integer("1. Masukkan Gaji Awal Bulanan (misal: 9000000): ")
    usia_awal = dapatkan_input_integer("2. Masukkan Usia Awal (misal: 28): ")
    usia_pensiun = dapatkan_input_integer("3. Masukkan Usia Pensiun (misal: 65): ")
    kenaikan_gaji_pa = dapatkan_input_float("4. Masukkan Kenaikan Gaji Tahunan (misal: 6): ")
    
    print("\n--- Harap periksa worksheet 'Goal' di Excel ---")
    
    # Hasil dari Excel
    # PERBAIKAN DI SINI: Menggunakan float agar desimal .66 tidak hilang
    total_akumulasi_dana = dapatkan_input_float("5. Masukkan Total Akumulasi Dana (angka 'Balance'): ")
    
    # Asumsi Aktuaria (Dipilih Manual)
    faktor_anuitas = dapatkan_input_float("6. Masukkan Faktor Anuitas Hidup ('a-dot-dot', misal: 13.8479): ")
    
    # --- TAHAP 2: LAKUKAN PERHITUNGAN AKHIR ---
    
    print("\nMenghitung...")
    
    # 2.1: Hitung Gaji Terakhir sebagai pembanding IRR
    try:
        masa_kerja = usia_pensiun - usia_awal
        gaji_terakhir_bulanan = gaji_awal_bulanan * math.pow(1 + (kenaikan_gaji_pa / 100), masa_kerja)
        
        # 2.2: Hitung Manfaat Pensiun Bulanan (IRR dalam Rupiah)
        manfaat_pensiun_bulanan = total_akumulasi_dana / (faktor_anuitas * 12)
        
        # 2.3: Hitung Rasio IRR (Persentase)
        irr_persen = (manfaat_pensiun_bulanan / gaji_terakhir_bulanan) * 100
    
    except Exception as e:
        print(f"GAGAL MELAKUKAN PERHITUNGAN. Error: {e}")
        return

    # --- TAHAP 3: CETAK LAPORAN HASIL & ANALISIS ---
    
    print("=" * 50)
    print("               HASIL AKHIR & ANALISIS (VERSI BENAR)")
    print("=" * 50)
    
    print("\n[PROYEKSI DI USIA PENSIUN]")
    print(f"  - Proyeksi Gaji Terakhir Anda  : Rp {gaji_terakhir_bulanan:,.0f} / bulan")
    print(f"  - Total Akumulasi Dana Pensiun : Rp {total_akumulasi_dana:,.2f}")
    
    print("\n[MANFAAT PENSIUN & IRR]")
    print(f"  - Manfaat Pensiun Bulanan (IRR): Rp {manfaat_pensiun_bulanan:,.0f} / bulan")
    print(f"  - INCOME REPLACEMENT RATIO (IRR): {irr_persen:.2f} %")
    
    print("\n[ANALISIS & KESIMPULAN]")
    if irr_persen < 40:
        print(f"  - TEMUAN: Hasil IRR {irr_persen:.2f}% masih JAUH DI BAWAH target ideal (70-80%).")
        print("  - KESIMPULAN: Desain program pensiun 'standar' (misal: iuran total 10%)")
        print("    TIDAK CUKUP untuk membiayai gaya hidup ideal saat pensiun.")
        print("\n  - REKOMENDASI: Peserta perlu menambah % iuran pribadi, memperpanjang")
        print("    masa kerja, atau mengambil portofolio investasi yang lebih agresif.")
    else:
        print(f"  - TEMUAN: Hasil IRR {irr_persen:.2f}% sudah cukup baik.")
        print("  - KESIMPULAN: Desain program pensiun ini sudah di jalur yang tepat.")
        
    print("=" * 50)
    print("Analisis Selesai.")

if __name__ == "__main__":
    main()