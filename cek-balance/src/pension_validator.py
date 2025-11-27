import pandas as pd
import numpy as np

class PensionValidator:
    def __init__(self, tmi_male_path, tmi_female_path):
        """
        Inisialisasi dengan path ke file CSV TMI 4.
        Struktur CSV: usia, qx, lx, dx, Dx, Cx, Nx, Mx
        """
        self.tmi_m = self._load_data(tmi_male_path)
        self.tmi_f = self._load_data(tmi_female_path)

    def _load_data(self, path):
        try:
            df = pd.read_csv(path)
            # Pastikan nama kolom standar untuk internal processing
            # Jika ada perbedaan case (misal Usia vs usia), kita standarisasi
            df.columns = [c.lower() for c in df.columns]
            
            # Mapping kolom penting ke nama standar
            rename_map = {
                'usia': 'Age',
                'qx': 'qx',
                'lx': 'lx'
            }
            # Rename jika ada kuncinya
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            return df
        except FileNotFoundError:
            print(f"Warning: File {path} not found. Using dummy data.")
            return self._create_dummy_tmi()

    def _create_dummy_tmi(self):
        # Dummy data generator sesuai struktur: usia,qx,lx,dx,Dx,Cx,Nx,Mx
        ages = np.arange(0, 112)
        
        # Gompertz law simple approximation for qx
        qx = 0.0001 * np.exp(0.09 * ages)
        qx = np.minimum(qx, 1.0)
        
        # Calculate lx based on qx starting with radiks 100,000
        lx = [100000.0]
        for q in qx[:-1]:
            lx.append(lx[-1] * (1 - q))
        lx = np.array(lx)
        
        dx = lx * qx
        
        # Kolom komutasi dummy (asumsi bunga 5% sekedar untuk isi struktur)
        v = 1 / 1.05
        Dx = lx * (v ** ages)
        Nx = np.cumsum(Dx[::-1])[::-1] # Sum from x to omega
        Cx = dx * (v ** (ages + 0.5))
        Mx = np.cumsum(Cx[::-1])[::-1]

        return pd.DataFrame({
            'Age': ages,
            'qx': qx,
            'lx': lx,
            'dx': dx,
            'Dx': Dx,
            'Cx': Cx,
            'Nx': Nx,
            'Mx': Mx
        })

    def calculate_actuarial_values(self, age, interest_rate, gender='m'):
        """
        Menghitung ulang faktor komutasi secara dinamis berdasarkan interest_rate input.
        Ini penting agar validasi rigorous, tidak bergantung pada bunga statis di file CSV.
        """
        df = self.tmi_m if gender == 'm' else self.tmi_f
        
        # Ambil slice data mulai dari umur perhitungan sampai akhir tabel
        # Agar index array mulai dari 0 untuk perhitungan v^t
        subset = df[df['Age'] >= age].copy().reset_index(drop=True)
        
        if subset.empty:
            return 0
        
        # Recalculate Commutation Functions dynamically
        # Dx = v^t * lx (dimana t adalah tahun berjalan dari usia sekarang)
        # Kita gunakan lx dari tabel, tapi diskon faktor disesuaikan dengan input
        
        # v^t di mana t=0, 1, 2...
        t = subset.index.values
        v_t = (1 + interest_rate) ** -(t)
        
        # Dx_new = lx * v^t
        # Note: Ini adalah Present Value dari 1 orang yang hidup di masa depan
        subset['Dx_calc'] = subset['lx'] * v_t
        
        # Nx = Sum(Dx)
        Nx_calc = subset['Dx_calc'].sum()
        Dx_at_age = subset['Dx_calc'].iloc[0]
        
        # Whole Life Annuity Due (Tahunan): ax = Nx / Dx
        if Dx_at_age == 0:
            return 0
            
        ax_annual = Nx_calc / Dx_at_age
        
        # Adjustment Woolhouse untuk Bulanan: ax(12) ≈ ax - 11/24
        ax_monthly = ax_annual - (11/24)
        
        return ax_monthly

    def simulate_jp_deficit(self, 
                            start_wage, 
                            years_of_service, 
                            salary_increase_rate, 
                            invest_return_rate, 
                            discount_rate,
                            retirement_age=56):
        """
        Melakukan simulasi sisi Aset vs Liabilitas
        """
        
        # --- 1. SISI ASET (AKUMULASI IURAN) ---
        wages = []
        # Asumsi Iuran JP: 3% (1% Pekerja + 2% Pemberi Kerja)
        contribution_rate = 0.03 
        
        current_wage = start_wage
        accumulated_fund = 0
        
        for t in range(years_of_service):
            # Gaji tahun ke-t
            wages.append(current_wage)
            
            # Iuran tahunan
            annual_contribution = current_wage * contribution_rate * 12
            
            # Pengembangan Iuran (Compound Interest)
            # Iuran diasumsikan masuk di akhir/tengah tahun, tapi simplifikasi: awal tahun
            # Lama pengembangan = (Tahun Pensiun - Tahun Kontribusi)
            periods_remaining = years_of_service - 1 - t
            
            # Future Value of Contribution
            fv_contribution = annual_contribution * ((1 + invest_return_rate) ** periods_remaining)
            accumulated_fund += fv_contribution
            
            # Kenaikan gaji untuk tahun depan
            current_wage = current_wage * (1 + salary_increase_rate)

        # --- 2. SISI LIABILITAS (NILAI SEKARANG MANFAAT) ---
        # Formula Manfaat JP: 1% x Masa Iur x Rata-rata Upah
        # Slide 17 menggunakan asumsi yang membuat manfaat terlihat rendah/timpang.
        # Biasanya menggunakan Rata-rata upah nominal (tanpa inflasi) untuk menunjukkan gap.
        avg_wage_nominal = np.mean(wages) 
        
        benefit_factor = 0.01
        monthly_benefit = benefit_factor * years_of_service * avg_wage_nominal
        annual_benefit = monthly_benefit * 12
        
        # Hitung Faktor Anuitas (Present Value of 1 unit benefit per year)
        # Menggunakan discount_rate (bukan investment return)
        annuity_factor_monthly = self.calculate_actuarial_values(
            age=retirement_age, 
            interest_rate=discount_rate, 
            gender='m' # Asumsi Pria (biasanya mortalitas lebih tinggi -> cost lebih rendah drpd wanita)
        )
        
        # Actuarial Present Value (APV) Liabilitas
        liability_pv = annual_benefit * annuity_factor_monthly
        
        unfunded = accumulated_fund - liability_pv
        
        return {
            "Gaji Awal": start_wage,
            "Gaji Akhir": wages[-1],
            "Rata-rata Gaji": avg_wage_nominal,
            "Masa Kerja": years_of_service,
            "Manfaat/Bulan": monthly_benefit,
            "Faktor Anuitas (ax_12)": annuity_factor_monthly,
            "Total Aset (Akumulasi)": accumulated_fund,
            "Total Liabilitas (PV)": liability_pv,
            "Gap (Surplus/Defisit)": unfunded,
            "Funding Ratio": (accumulated_fund / liability_pv) * 100 if liability_pv != 0 else 0
        }

# --- Block Testing ---
if __name__ == "__main__":
    # Ganti path sesuai lokasi file Anda
    validator = PensionValidator("data/tmi_4_m.csv", "data/tmi_4_f.csv")
    
    # Validasi Kasus Slide 17:
    # Gaji 2.5 Juta -> Unfunded (311 Juta)
    # Kita coba cari parameter implisitnya
    print("--- VALIDASI SLIDE 17 (Gaji 2.5 Juta) ---")
    
    # Parameter Asumsi (Trial and Error untuk mendekati angka slide)
    # Slide ini sepertinya menggunakan asumsi yang sangat konservatif pada liabilitas (bunga rendah)
    # atau agresif pada kenaikan gaji.
    params = {
        "start_wage": 2_500_000,
        "years_of_service": 32,      # Asumsi standar masa kerja penuh
        "salary_increase_rate": 0.05, # Kenaikan gaji per tahun
        "invest_return_rate": 0.06,   # Hasil investasi aset
        "discount_rate": 0.05,        # Bunga teknis untuk menghitung PV Liabilitas
        "retirement_age": 56
    }
    
    res = validator.simulate_jp_deficit(**params)
    
    for k, v in res.items():
        if isinstance(v, float):
            print(f"{k}: {v:,.2f}")
        else:
            print(f"{k}: {v}")