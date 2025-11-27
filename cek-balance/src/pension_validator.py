import pandas as pd
import numpy as np
import numpy_financial as npf

class PensionValidator:
    def __init__(self, tmi_male_path, tmi_female_path):
        """
        Inisialisasi dengan path ke file CSV TMI 4.
        Struktur CSV diasumsikan memiliki kolom 'Age' dan 'qx' (peluang kematian).
        """
        try:
            self.tmi_m = pd.read_csv(tmi_male_path)
            self.tmi_f = pd.read_csv(tmi_female_path)
        except FileNotFoundError:
            # Fallback jika file belum ada di environment lokal user saat testing
            print("Warning: TMI files not found. Using dummy mortality data.")
            self.tmi_m = self._create_dummy_tmi()
            self.tmi_f = self._create_dummy_tmi()

    def _create_dummy_tmi(self):
        # Dummy data generator menyerupai kurva mortalitas (Gompertz law simplified)
        ages = np.arange(0, 111)
        qx = 0.0001 * np.exp(0.09 * ages)
        qx = np.minimum(qx, 1.0)
        return pd.DataFrame({'Age': ages, 'qx': qx})

    def calculate_annuity_factor(self, age, interest_rate, gender='m'):
        """
        Menghitung faktor anuitas seumur hidup (whole life annuity due) 
        pembayaran bulanan a_double_dot_x^(12).
        
        Rumus pendekatan: a_double_dot_x^(12) ≈ a_double_dot_x - 11/24
        """
        df = self.tmi_m if gender == 'm' else self.tmi_f
        
        # Filter mulai dari usia pensiun
        df_calc = df[df['Age'] >= age].copy().reset_index(drop=True)
        
        # Hitung Probability of Survival (tpx)
        # p_x = 1 - q_x
        df_calc['px'] = 1 - df_calc['qx']
        df_calc['tpx'] = df_calc['px'].cumprod().shift(1).fillna(1)
        
        # Discount factor v^t
        df_calc['t'] = df_calc.index
        df_calc['v_t'] = (1 + interest_rate) ** (-df_calc['t'])
        
        # Whole life annuity factor (tahunan)
        ax = np.sum(df_calc['v_t'] * df_calc['tpx'])
        
        # Adjustment ke bulanan (Woolhouse approximation standard)
        ax_monthly = ax - (11/24)
        
        return ax_monthly

    def simulate_jp_deficit(self, 
                            start_wage, 
                            years_of_service, 
                            salary_increase_rate, 
                            invest_return_rate, 
                            discount_rate,
                            retirement_age=56):
        """
        Mereplikasi Tabel di Slide 17.
        """
        
        # 1. Hitung Proyeksi Gaji & Iuran (Sisi Aset)
        wages = []
        contributions = [] # 3% total (1% pekerja + 2% pemberi kerja)
        jp_contribution_rate = 0.03
        
        current_wage = start_wage
        
        for year in range(years_of_service):
            wages.append(current_wage)
            contributions.append(current_wage * jp_contribution_rate * 12) # Iuran setahun
            current_wage = current_wage * (1 + salary_increase_rate)
            
        # Hitung Akumulasi Dana (Future Value of Contributions)
        accumulated_fund = 0
        for i, cont in enumerate(contributions):
            # Masa pengembangan: dari tahun kontribusi sampai pensiun
            periods = years_of_service - 1 - i 
            accumulated_fund += cont * ((1 + invest_return_rate) ** periods)

        # 2. Hitung Manfaat Pensiun (Sisi Liabilitas)
        # Rumus JP: 1% x Masa Iur x Rata-rata Upah Tertimbang
        # Note: Slide tidak merinci 'Tertimbang', kita pakai rata-rata sederhana atau inflasi adjusted
        # Asumsi konservatif: Rata-rata gaji selama masa kerja (Career Average)
        # Namun seringkali 'Tertimbang' diartikan revalued career average.
        
        # Kita gunakan Career Average yang disesuaikan dengan inflasi (invest_return assumption sebagai proxy revaluasi)
        # Atau simple average dari nominal history (ini akan menghasilkan manfaat kecil).
        # Mari coba Simple Average dari nominal (sesuai praktek BPJS TK biasanya untuk estimasi kasar)
        avg_wage = np.mean(wages)
        
        monthly_benefit = 0.01 * years_of_service * avg_wage
        yearly_benefit = monthly_benefit * 12
        
        # 3. Hitung Nilai Tunai Manfaat (Actuarial Present Value)
        # Menggunakan TMI 4 Male sebagai proxy (biasanya pria lebih boros anuitasnya karena istri lebih muda/hidup lama, 
        # tapi untuk single life kita pakai Male dulu sesuai data umum pekerja)
        annuity_factor = self.calculate_annuity_factor(retirement_age, discount_rate, gender='m')
        
        benefit_value_pv = yearly_benefit * annuity_factor
        
        unfunded = accumulated_fund - benefit_value_pv
        
        return {
            "Upah Awal": start_wage,
            "Akumulasi Dana (Asset)": accumulated_fund,
            "Nilai Manfaat (Liabilitas)": benefit_value_pv,
            "Selisih (Unfunded)": unfunded,
            "Annuity Factor": annuity_factor,
            "Monthly Benefit": monthly_benefit
        }

# --- Block Testing (Simulation) ---
if __name__ == "__main__":
    # Setup Paths (Sesuaikan dengan struktur repo Anda)
    tmi_m_path = "data/tmi_4_m.csv"
    tmi_f_path = "data/tmi_4_f.csv"
    
    validator = PensionValidator(tmi_m_path, tmi_f_path)
    
    # --- REVERSE ENGINEERING SLIDE 17 ---
    # Kita coba cari parameter asumsi yang menghasilkan angka di Slide 17
    # Baris 1 Tabel Slide 17:
    # Upah Awal: 2,500,000
    # Akumulasi: ~249,783,000
    # Nilai Manfaat: ~561,752,000
    
    print("--- Validasi Slide 17 (Trial Run) ---")
    
    # Asumsi yang harus kita 'tebak' atau kalibrasi untuk mencocokkan angka slide:
    assumed_years = 32 # Tebakan masa kerja (biasa dipakai simulasi standar)
    assumed_sal_inc = 0.05 # Kenaikan gaji 5%
    assumed_inv_ret = 0.06 # Return investasi 6%
    assumed_disc_rate = 0.05 # Discount rate untuk anuitas 5% (biasanya yield SBN tenor panjang)
    
    result = validator.simulate_jp_deficit(
        start_wage=2_500_000, 
        years_of_service=assumed_years,
        salary_increase_rate=assumed_sal_inc,
        invest_return_rate=assumed_inv_ret,
        discount_rate=assumed_disc_rate
    )
    
    print(f"Input Upah Awal: {result['Upah Awal']:,.0f}")
    print(f"Calculated Asset: {result['Akumulasi Dana (Asset)']:,.0f}")
    print(f"Calculated Liability: {result['Nilai Manfaat (Liabilitas)']:,.0f}")
    print(f"Calculated Unfunded: {result['Selisih (Unfunded)']:,.0f}")
    print("-" * 30)
    print("Target Slide 17:")
    print("Asset: ~249,783,000 | Liabilitas: ~561,752,000")