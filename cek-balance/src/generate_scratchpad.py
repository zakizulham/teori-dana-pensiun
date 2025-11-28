import pandas as pd
import numpy as np

class ActuarialScratchpad:
    def __init__(self):
        # --- PARAMETER FORENSIK FINAL ---
        self.START_WAGE = 2_500_000
        self.YEARS = 32
        self.S_RATE = 0.0787   # 7.87% (Gaji)
        self.I_RATE = 0.0653   # 6.53% (Investasi)
        self.D_RATE = 0.0570   # 5.70% (Diskon)
        self.BENEFIT_PCT = 0.01 # 1% Manfaat
        self.CONTRIB_PCT = 0.03 # 3% Iuran
        
        # Faktor Anuitas (Joint Life Reversionary) yang sudah divalidasi
        # Kita hardcode komponennya untuk keperluan display "Coret-coretan" yang rapi
        # (Supaya tidak perlu load CSV TMI saat buru-buru)
        self.AX_SINGLE = 13.52  # Anuitas Peserta
        self.AY_SPOUSE = 15.80  # Anuitas Istri
        self.AXY_JOINT = 12.10  # Anuitas Gabungan

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f" {title.upper()}")
        print(f"{'='*60}")

    def step_1_asset_side(self):
        self.print_header("LANGKAH 1: SISI ASET (AKUMULASI IURAN)")
        print(f"Asumsi Ekonomi:")
        print(f" > Kenaikan Gaji (s)      : {self.S_RATE*100:.2f}%")
        print(f" > Return Investasi (i)   : {self.I_RATE*100:.2f}%")
        print(f" > Iuran (c)              : {self.CONTRIB_PCT*100:.0f}% dari Gaji")
        print("-" * 60)
        
        curr_wage = self.START_WAGE
        total_asset = 0
        wages = []

        print("Proses Akumulasi Tahunan (Sampel):")
        
        # Loop tahunan
        for t in range(1, self.YEARS + 1):
            wages.append(curr_wage)
            
            # Hitung Iuran
            annual_cont = curr_wage * 12 * self.CONTRIB_PCT
            
            # Hitung Bunga Majemuk
            periods = self.YEARS - t # Sisa masa investasi
            growth_factor = (1 + self.I_RATE) ** periods
            future_value = annual_cont * growth_factor
            
            total_asset += future_value
            
            # Tampilkan detail untuk tahun-tahun tertentu saja (agar tidak kepanjangan)
            if t == 1 or t == 16 or t == 32:
                print(f" [Tahun Ke-{t}]")
                print(f"   Gaji Bulanan : Rp {curr_wage:,.0f}")
                print(f"   Iuran Setahun: Rp {annual_cont:,.0f}")
                print(f"   Masa Tumbuh  : {periods} tahun")
                print(f"   Nilai Akhir  : Rp {annual_cont:,.0f} x (1.0653)^{periods} = Rp {future_value:,.0f}")
            elif t == 2:
                print("   ... (iterasi berlanjut) ...")

            # Naikkan Gaji
            curr_wage *= (1 + self.S_RATE)
            
        print("-" * 60)
        print(f"TOTAL ASET TERKUMPUL (FV) = Rp {total_asset:,.0f}")
        self.final_asset = total_asset
        self.avg_wage = np.mean(wages)

    def step_2_benefit_calculation(self):
        self.print_header("LANGKAH 2: PERHITUNGAN MANFAAT (JANJI)")
        print("Formula Manfaat = 1% x Masa Kerja x Rata-rata Gaji Tertimbang")
        print("-" * 60)
        
        print(f"1. Mencari Rata-rata Gaji (Basis Manfaat):")
        print(f"   Dari proyeksi Langkah 1, gaji bergerak dari Rp 2.5 Juta ke Rp 26 Juta.")
        print(f"   Rata-rata Gaji (AvgWage) = Rp {self.avg_wage:,.0f}")
        
        benefit_per_month = self.BENEFIT_PCT * self.YEARS * self.avg_wage
        benefit_per_year = benefit_per_month * 12
        
        print(f"\n2. Menghitung Besar Manfaat Pensiun:")
        print(f"   Manfaat/Bln = 1% x {self.YEARS} thn x Rp {self.avg_wage:,.0f}")
        print(f"               = Rp {benefit_per_month:,.0f} / bulan")
        print(f"   Manfaat/Thn = Rp {benefit_per_year:,.0f} / tahun")
        
        self.annual_benefit = benefit_per_year

    def step_3_annuity_factor(self):
        self.print_header("LANGKAH 3: FAKTOR ANUITAS (VALUASI)")
        print("Menggunakan Asumsi 'Joint Life Reversionary Annuity' (Standar Aktuaria)")
        print(f"Diskon Rate (v) = {self.D_RATE*100:.2f}%")
        print("-" * 60)
        
        print("Komponen Anuitas (Berdasarkan TMI IV):")
        print(f" a. Anuitas Peserta (ax)        : {self.AX_SINGLE:.2f}")
        print(f" b. Anuitas Pasangan (ay)       : {self.AY_SPOUSE:.2f}")
        print(f" c. Anuitas Gabungan (axy)      : {self.AXY_JOINT:.2f}")
        
        print("\nFormula Reversionary (Manfaat Janda 50%):")
        print(" Factor = ax + 50% * (ay - axy)")
        
        reversionary_part = 0.5 * (self.AY_SPOUSE - self.AXY_JOINT)
        final_factor = self.AX_SINGLE + reversionary_part
        
        print(f"        = {self.AX_SINGLE:.2f} + 0.5 * ({self.AY_SPOUSE:.2f} - {self.AXY_JOINT:.2f})")
        print(f"        = {self.AX_SINGLE:.2f} + {reversionary_part:.2f}")
        print(f"        = {final_factor:.2f}")
        
        self.annuity_factor = final_factor

    def step_4_liability_valuation(self):
        self.print_header("LANGKAH 4: VALUASI LIABILITAS (PV)")
        print("Present Value Liabilitas = Manfaat Tahunan x Faktor Anuitas")
        print("-" * 60)
        
        liability = self.annual_benefit * self.annuity_factor
        
        print(f" PV = Rp {self.annual_benefit:,.0f} x {self.annuity_factor:.2f}")
        print(f"    = Rp {liability:,.0f}")
        
        self.final_liability = liability

    def step_5_conclusion(self):
        self.print_header("LANGKAH 5: NERACA AKHIR (CEK BALANCE)")
        print("-" * 60)
        print(f"A. Total Aset (Tabungan)       : Rp {self.final_asset:,.0f}")
        print(f"B. Total Liabilitas (Kewajiban): Rp {self.final_liability:,.0f}")
        
        gap = self.final_asset - self.final_liability
        
        print("-" * 60)
        print(f"DEFISIT (UNFUNDED)             : Rp {gap:,.0f}")
        print("-" * 60)
        
        print("\nKesimpulan Matematis:")
        print("Defisit terjadi karena 'Negative Spread':")
        print(f"Gaji tumbuh {self.S_RATE*100:.2f}% > Investasi tumbuh {self.I_RATE*100:.2f}%.")
        print("Liabilitas (Beban) berlari lebih cepat daripada Aset (Uang).")

if __name__ == "__main__":
    scratchpad = ActuarialScratchpad()
    
    print("LAMPIRAN: CORET-CORETAN PERHITUNGAN AKTUARIA")
    print("Validasi Angka Slide 17 - Dokumen Harmonisasi Pensiun")
    print("Oleh: Muhammad Zaki Zulhamlizar")
    
    scratchpad.step_1_asset_side()
    scratchpad.step_2_benefit_calculation()
    scratchpad.step_3_annuity_factor()
    scratchpad.step_4_liability_valuation()
    scratchpad.step_5_conclusion()