import pandas as pd
import numpy as np
from scipy.optimize import brentq 

class PensionReverseEngineer:
    def __init__(self, tmi_male_path, tmi_female_path):
        self.tmi_m = self._load_data(tmi_male_path)
        self.tmi_f = self._load_data(tmi_female_path)

    def _load_data(self, path):
        # (Sama seperti sebelumnya, handling load data)
        try:
            df = pd.read_csv(path)
            df.columns = [c.lower() for c in df.columns]
            rename_map = {'usia': 'Age', 'qx': 'qx', 'lx': 'lx'}
            df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
            return df
        except FileNotFoundError:
            return self._create_dummy_tmi()

    def _create_dummy_tmi(self):
        ages = np.arange(0, 115)
        qx = 0.0001 * np.exp(0.092 * ages)
        qx = np.minimum(qx, 1.0)
        lx = [100000.0]
        for q in qx[:-1]:
            lx.append(lx[-1] * (1 - q))
        return pd.DataFrame({'Age': ages, 'qx': qx, 'lx': np.array(lx)})

    def calculate_annuity_factors_raw(self, age_m, age_f, interest_rate, benefit_growth=0.0):
        """
        Menghitung ax (single), ay (spouse single), axy (joint) secara terpisah
        sebelum digabung. Ini penting untuk rigorous math.
        """
        # Slice Data
        m_data = self.tmi_m[self.tmi_m['Age'] >= age_m].copy().reset_index(drop=True)
        f_data = self.tmi_f[self.tmi_f['Age'] >= age_f].copy().reset_index(drop=True)
        min_len = min(len(m_data), len(f_data))
        
        # Probabilitas tpx
        tpx_m = m_data['lx'].values[:min_len] / m_data['lx'].iloc[0]
        tpx_f = f_data['lx'].values[:min_len] / f_data['lx'].iloc[0]
        tpx_joint = tpx_m * tpx_f
        
        # Discount Factor (Real Rate)
        t = np.arange(min_len)
        v_t = ((1 + benefit_growth) / (1 + interest_rate)) ** t
        
        # Hitung Anuitas Tahunan (Due)
        ax_annual = np.sum(v_t * tpx_m)
        ay_annual = np.sum(v_t * tpx_f)
        axy_annual = np.sum(v_t * tpx_joint)
        
        return ax_annual, ay_annual, axy_annual

    def calculate_liability(self, start_wage, years, salary_inc, discount_rate, indexation, survivor_pct):
        """
        Menghitung Liabilitas (PV Manfaat) berdasarkan parameter input.
        """
        # 1. Hitung Rata-rata Gaji (Basis Manfaat)
        # Menggunakan deret geometri untuk efisiensi
        # Sum = a * (r^n - 1) / (r - 1)
        if salary_inc == 0:
            avg_wage = start_wage
        else:
            r = 1 + salary_inc
            total_wage = start_wage * (r**years - 1) / (r - 1)
            avg_wage = total_wage / years
            
        # 2. Rumus Manfaat Tahunan
        annual_benefit = (0.01 * years * avg_wage) * 12
        
        # 3. Faktor Anuitas (Woolhouse Corrected)
        # Asumsi Pria 56, Istri 51 (Gap 5 tahun)
        ax, ay, axy = self.calculate_annuity_factors_raw(56, 51, discount_rate, indexation)
        
        # Rumus Rigorous: (ax - 11/24) + Pct * (ay - axy)
        # Bagian reversionary (ay - axy) tidak dikurangi 11/24 karena saling menghilangkan
        annuity_factor = (ax - 11/24) + survivor_pct * (ay - axy)
        
        return annual_benefit * annuity_factor

    def calculate_asset(self, start_wage, years, salary_inc, invest_return):
        """
        Menghitung Akumulasi Aset (FV Iuran)
        """
        accumulated = 0
        contribution_rate = 0.03 # 3% Total
        current_wage = start_wage
        
        for t in range(years):
            annual_cont = current_wage * contribution_rate * 12
            periods = years - 1 - t
            accumulated += annual_cont * ((1 + invest_return) ** periods)
            current_wage *= (1 + salary_inc)
            
        return accumulated

    def solve_assumptions(self, target_asset, target_liability, start_wage=2500000, years=32):
        print(f"--- REVERSE ENGINEERING START ---")
        print(f"Target Asset     : {target_asset:,.0f}")
        print(f"Target Liability : {target_liability:,.0f}")
        
        # --- PHASE 1: SOLVE SALARY INCREASE ---
        # Kita fix discount rate di angka wajar aktuaria (misal 5.5% atau 6%)
        # Kita fix survivor benefit 50% (sesuai regulasi umum)
        # Kita fix indexation 0% (karena simulasi defisit biasanya pakai nominal)
        
        fixed_discount = 0.057  # Coba 5.7% (Yield SBN Tenor Panjang rata-rata)
        fixed_survivor = 0.5    # 50%
        fixed_indexation = 0.0
        
        def liab_error(s_inc):
            calc = self.calculate_liability(start_wage, years, s_inc, fixed_discount, fixed_indexation, fixed_survivor)
            return calc - target_liability
            
        # Cari salary increase (s) antara 0% sampai 15%
        try:
            implied_salary_inc = brentq(liab_error, 0.0, 0.15)
        except ValueError:
            print("Gagal menemukan Salary Increase yang pas. Cek range discount rate.")
            return None

        print(f"\n[PHASE 1] Found Salary Increase!")
        print(f"-> Agar Liabilitas {target_liability:,.0f} dengan Diskon {fixed_discount:.1%}:")
        print(f"-> Implied Salary Increase = {implied_salary_inc:.2%}")
        
        # --- PHASE 2: SOLVE INVESTMENT RETURN ---
        # Sekarang kita punya implied_salary_inc, kita cari return investasi
        # agar asetnya match 249 Jt
        
        def asset_error(i_ret):
            calc = self.calculate_asset(start_wage, years, implied_salary_inc, i_ret)
            return calc - target_asset
            
        try:
            implied_invest_ret = brentq(asset_error, 0.0, 0.20)
        except ValueError:
            print("Gagal menemukan Invest Return yang pas.")
            return None
            
        print(f"\n[PHASE 2] Found Investment Return!")
        print(f"-> Agar Aset {target_asset:,.0f} dengan Salary Inc {implied_salary_inc:.2%}:")
        print(f"-> Implied Investment Return = {implied_invest_ret:.2%}")
        
        # --- VERIFIKASI LOGIKA EKONOMI ---
        spread = implied_invest_ret - implied_salary_inc
        print(f"\n[PHASE 3] Economic Logic Check")
        print(f"Spread (Invest - Salary) = {spread:.2%}")
        
        status = "✅ LOGIS (Invest > Salary)" if spread > 0 else "⚠️ ANEH (Invest < Salary)"
        print(f"Status Model: {status}")
        
        return {
            "salary_inc": implied_salary_inc,
            "invest_ret": implied_invest_ret,
            "discount_rate": fixed_discount,
            "spread": spread
        }

if __name__ == "__main__":
    # Inisialisasi (sesuaikan path)
    solver = PensionReverseEngineer("data/tmi_4_m.csv", "data/tmi_4_f.csv")
    
    # Target Data dari Slide 17 (Baris Gaji 2.5 Juta) 
    TARGET_ASSET = 249_783_000
    TARGET_LIAB  = 561_752_000
    
    assumptions = solver.solve_assumptions(TARGET_ASSET, TARGET_LIAB)