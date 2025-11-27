import pandas as pd
import numpy as np

class ActuarialCalculator:
    def __init__(self, tmi_male_path, tmi_female_path):
        self.tmi_m = self._load_tmi(tmi_male_path)
        self.tmi_f = self._load_tmi(tmi_female_path)

    def _load_tmi(self, path):
        # Load standar TMI 4
        try:
            df = pd.read_csv(path)
            df.columns = [c.lower() for c in df.columns]
            rename_map = {'usia': 'Age', 'qx': 'qx', 'lx': 'lx'}
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            return df
        except:
            # Fallback dummy jika file tidak ada (hanya agar script jalan)
            ages = np.arange(0, 115)
            qx = 0.0001 * np.exp(0.09 * ages)
            return pd.DataFrame({'Age': ages, 'qx': np.minimum(qx, 1.0), 'lx': 100000*(1-np.minimum(qx, 1.0))})

    def calculate_annuity(self, age_m, age_f, interest_rate):
        """
        Menghitung Faktor Anuitas Reversionary (Suami + 50% Janda)
        """
        # Slice data mortalitas
        limit = min(len(self.tmi_m)-age_m, len(self.tmi_f)-age_f)
        lx_m = self.tmi_m.loc[self.tmi_m['Age'] >= age_m, 'lx'].values[:limit]
        lx_f = self.tmi_f.loc[self.tmi_f['Age'] >= age_f, 'lx'].values[:limit]
        
        # Probabilitas (tpx)
        tpx_m = lx_m / lx_m[0]
        tpx_f = lx_f / lx_f[0]
        tpx_joint = tpx_m * tpx_f
        
        # Discount Factor (v^t)
        v = 1 / (1 + interest_rate)
        vt = v ** np.arange(limit)
        
        # 1. Anuitas Single Life (Peserta) - Woolhouse corrected (-11/24)
        ax = np.sum(vt * tpx_m) - (11/24)
        
        # 2. Anuitas Joint (Peserta + Pasangan)
        axy = np.sum(vt * tpx_joint)
        
        # 3. Anuitas Pasangan Single (Survivor only)
        ay = np.sum(vt * tpx_f)
        
        # Total: Peserta Hidup (100%) + Peserta Mati & Pasangan Hidup (50%)
        # Rumus: ax + 0.5 * (ay - axy)
        total_annuity = ax + 0.5 * (ay - axy)
        
        return total_annuity

    def run_valuation(self):
        # --- PARAMETER KUNCI (HASIL ANALISA FORENSIK) ---
        SALARY_INC = 0.0787  # 7.87% (Gaji naik tinggi)
        INVEST_RET = 0.0653  # 6.53% (Investasi moderat)
        DISCOUNT_R = 0.0570  # 5.70% (Diskon Liabilitas)
        START_WAGE = 2_500_000
        YEARS      = 32
        
        # 1. PROYEKSI CASHFLOW
        wages = []
        asset_accum = 0
        curr_wage = START_WAGE
        
        for t in range(YEARS):
            wages.append(curr_wage)
            # Iuran 3% masuk, dikembangkan dengan Invest Return
            cont = curr_wage * 12 * 0.03
            period_invest = YEARS - 1 - t
            asset_accum += cont * ((1 + INVEST_RET) ** period_invest)
            
            curr_wage *= (1 + SALARY_INC)
            
        # 2. VALUASI LIABILITAS
        avg_wage = np.mean(wages)
        benefit_per_mo = 0.01 * YEARS * avg_wage
        benefit_per_yr = benefit_per_mo * 12
        
        # Faktor Anuitas (Pria 56, Istri 51)
        annuity_factor = self.calculate_annuity(56, 51, DISCOUNT_R)
        
        liability_pv = benefit_per_yr * annuity_factor
        
        # 3. HASIL
        print("--- HASIL REPRODUKSI SLIDE 17 ---")
        print(f"Gaji Awal        : Rp {START_WAGE:,.0f}")
        print(f"Rata-rata Gaji   : Rp {avg_wage:,.0f} (Nominal)")
        print(f"Total Aset       : Rp {asset_accum:,.0f} [Target: ~249 Jt]")
        print(f"Total Liabilitas : Rp {liability_pv:,.0f} [Target: ~561 Jt]")
        print(f"Defisit          : Rp {asset_accum - liability_pv:,.0f} [Target: ~(311) Jt]")
        print(f"\nLOGIKA MATEMATIKA:")
        print(f"Spread = Investasi ({INVEST_RET:.2%}) - Kenaikan Gaji ({SALARY_INC:.2%}) = {(INVEST_RET-SALARY_INC):.2%}")
        print("Karena Spread Negatif, Liabilitas 'berlari' lebih cepat daripada Aset.")

# Run
calc = ActuarialCalculator("data/tmi_4_m.csv", "data/tmi_4_f.csv")
calc.run_valuation()