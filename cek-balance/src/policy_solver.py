import pandas as pd
import numpy as np
from scipy.optimize import brentq

class PolicySolver:
    def __init__(self):
        # Asumsi Forensik Slide 17 (Kondisi Buruk)
        self.s_rate = 0.0787   # Gaji naik 7.87%
        self.start_wage = 2_500_000
        self.years = 32
        self.annuity_factor = 14.32
        
        # Target Kebijakan Slide 22
        self.target_contribution = 0.09  # Iuran 9%
        self.target_accrual = 0.015      # Manfaat 1.5%

    def calculate_balance(self, i_rate):
        # 1. Hitung Liabilitas (Tetap, tidak dipengaruhi investasi)
        wages = [self.start_wage * ((1 + self.s_rate) ** t) for t in range(self.years)]
        avg_wage = np.mean(wages)
        liability = (self.target_accrual * self.years * avg_wage * 12) * self.annuity_factor
        
        # 2. Hitung Aset (Dipengaruhi investasi i_rate)
        asset = 0
        curr_w = self.start_wage
        for t in range(self.years):
            cont = curr_w * 12 * self.target_contribution # 9%
            periods = self.years - 1 - t
            asset += cont * ((1 + i_rate) ** periods)
            curr_w *= (1 + self.s_rate)
            
        return asset - liability

    def solve_required_return(self):
        print("--- MENCARI ASUMSI IMPLISIT PEMERINTAH ---")
        print(f"Target Iuran   : {self.target_contribution*100}%")
        print(f"Target Manfaat : {self.target_accrual*100}%")
        print(f"Kenaikan Gaji  : {self.s_rate*100}% (Tetap Buruk)")
        
        # Cari i_rate yang membuat Asset - Liability = 0
        # Kita cari di range 6% sampai 10%
        try:
            implied_roi = brentq(self.calculate_balance, 0.06, 0.10)
            
            print("-" * 40)
            print(f"Investasi Lama (Slide 17)     : 6.53%")
            print(f"Investasi Baru (Agar Cukup 9%): {implied_roi*100:.2f}%")
            print("-" * 40)
            
            diff = implied_roi - 0.0653
            print(f"KESIMPULAN:")
            print(f"Pemerintah hanya perlu menaikkan kinerja investasi sebesar +{diff*100:.2f}%")
            print(f"dari 6.53% menjadi {implied_roi*100:.2f}% agar angka 9% menjadi valid.")
            
        except ValueError:
            print("Gagal menemukan solusi dalam range wajar.")

if __name__ == "__main__":
    solver = PolicySolver()
    solver.solve_required_return()