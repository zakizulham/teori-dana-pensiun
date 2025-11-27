import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIG ---
st.set_page_config(page_title="Kalkulator Ekuivalensi Aktuaria", layout="centered")

st.title("🧮 Kalkulator Ekuivalensi Aktuaria")
st.markdown("""
Aplikasi ini menghitung **Titik Ekuilibrium Presisi**: Berapa persisnya iuran yang harus dibayar untuk membiayai tingkat manfaat tertentu?
""")

# --- 1. PARAMETER INPUT ---
st.sidebar.header("Parameter Asumsi")
st.sidebar.caption("Default disesuaikan dengan temuan forensik Slide 17")

# Asumsi Ekonomi (Forensik Slide 17)
s_rate = st.sidebar.number_input("Kenaikan Gaji Tahunan (%)", 0.0, 15.0, 7.87, 0.01) / 100
i_rate = st.sidebar.number_input("Return Investasi Tahunan (%)", 0.0, 15.0, 6.53, 0.01) / 100

# Asumsi Peserta
start_wage = 2_500_000
years = 32
annuity_factor_implied = 14.32  # Kalibrasi dari Slide 17

# INPUT TARGET (YANG DITANYAKAN)
st.subheader("🎯 Input Target Kebijakan")
target_accrual_rate = st.number_input(
    "Target Accrual Rate / Manfaat (%)", 
    min_value=0.5, max_value=3.0, value=1.5, step=0.1,
    help="Slide 22 mengusulkan kenaikan manfaat menjadi 1.5%"
) / 100

# --- 2. CALCULATION ENGINE (SOLVER) ---
def solve_required_contribution(target_accrual, s, i):
    # A. Hitung Sisi Liabilitas (Beban)
    # Proyeksi Gaji
    wages = [start_wage * ((1 + s) ** t) for t in range(years)]
    avg_wage = np.mean(wages)
    
    # Total Liabilitas = (Accrual * Masa Kerja * Rata2 Gaji * 12) * Anuitas
    liability = (target_accrual * years * avg_wage * 12) * annuity_factor_implied
    
    # B. Hitung "Kekuatan Aset" per 1% Iuran
    # Berapa aset yang terkumpul jika kita menabung 1% gaji setiap bulan?
    asset_per_1pct = 0
    curr_w = start_wage
    for t in range(years):
        cont_1pct = curr_w * 12 * 0.01
        periods = years - 1 - t
        asset_per_1pct += cont_1pct * ((1 + i) ** periods)
        curr_w *= (1 + s)
        
    # C. Solve for Equilibrium
    # Required % = Liability / Asset_per_1%
    # Contoh: Liabilitas 1000, Aset(1%) 100. Maka butuh 10x lipat (10%).
    # Nilai required_pct ini SUDAH dalam format persentase (misal 10.11)
    required_pct = (liability / asset_per_1pct)
    
    # FIX: Hapus pengalian * 100 di sini karena required_pct sudah merepresentasikan angka persen
    return required_pct, liability, asset_per_1pct * 100

# Hitung untuk Target User (1.5%)
req_rate_target, liab_target, asset_100pct = solve_required_contribution(target_accrual_rate, s_rate, i_rate)

# Hitung untuk Existing (1.0%)
req_rate_base, liab_base, _ = solve_required_contribution(0.01, s_rate, i_rate)

# --- 3. DISPLAY RESULT ---

st.divider()
st.subheader(f"✅ Hasil Perhitungan Ekuilibrium")

# Metric Utama
col1, col2 = st.columns(2)
with col1:
    st.info("Jika Manfaat (Accrual Rate) = 1.0% (Saat Ini)")
    st.metric("Iuran Wajar (Equilibrium)", f"{req_rate_base:.2f}%", help="Ini adalah biaya murni untuk manfaat 1%")

with col2:
    st.success(f"Jika Manfaat (Accrual Rate) = {target_accrual_rate*100:.1f}% (Target)")
    st.metric("Iuran Wajar (Equilibrium)", f"{req_rate_target:.2f}%", 
              delta=f"{req_rate_target - 9.0:.2f}% vs Usulan 9%", delta_color="inverse")

st.markdown(f"""
**Artinya:** Untuk memberikan manfaat pensiun sebesar **{target_accrual_rate*100}%** per tahun masa kerja, 
secara matematika iuran yang **WAJIB** dibayar adalah **{req_rate_target:.2f}%**.
""")

# --- 4. SCENARIO COMPARISON TABLE ---
st.divider()
st.subheader("📊 Perbandingan Skenario (Head-to-Head)")

# Skenario Usulan Slide 22 (Iuran 9%, Manfaat 1.5%)
# Kita hitung aset manual: Aset Full (100%) * 9%
asset_proposal = (asset_100pct / 100) * 9.0 
funding_ratio_proposal = (asset_proposal / liab_target) * 100

scenarios = {
    "Metrik": ["Iuran (Pemasukan)", "Manfaat (Pengeluaran)", "Total Liabilitas", "Total Aset", "Status Dana", "Funding Ratio"],
    "Kondisi Saat Ini (Slide 17)": [
        "3.00%", 
        "1.00%", 
        f"Rp {liab_base:,.0f}", 
        f"Rp {(asset_100pct/100)*3.0:,.0f}", 
        "DEFISIT PARAH", 
        f"{((asset_100pct/100)*3.0 / liab_base)*100:.1f}%"
    ],
    "Usulan Pemerintah (Slide 22)": [
        "9.00%", 
        "1.50%", 
        f"Rp {liab_target:,.0f}", 
        f"Rp {asset_proposal:,.0f}", 
        "DEFISIT RINGAN" if req_rate_target > 9.0 else "SURPLUS", 
        f"{funding_ratio_proposal:.1f}%"
    ],
    "Ekuilibrium Matematis (Ideal)": [
        f"**{req_rate_target:.2f}%**", 
        f"{target_accrual_rate*100:.2f}%", 
        f"Rp {liab_target:,.0f}", 
        f"Rp {liab_target:,.0f}", 
        "SEIMBANG (MATCH)", 
        "100.0%"
    ]
}

df_compare = pd.DataFrame(scenarios)
st.table(df_compare.set_index("Metrik"))

# --- 5. KESIMPULAN ANALIS ---
st.warning("📝 Catatan Analis:")

gap_slide22 = req_rate_target - 9.0
if gap_slide22 > 0:
    st.write(f"""
    Meskipun iuran dinaikkan menjadi **9%** (Slide 22), perhitungan menunjukkan angka tersebut **BELUM CUKUP** untuk membiayai manfaat **1.5%** secara penuh (kurang **{gap_slide22:.2f}%**).
    
    Ini menjelaskan mengapa di Slide 22 tertulis "Penyesuaian dilakukan secara bertahap". 
    Angka 9% kemungkinan adalah target jangka menengah, atau asumsi investasi Pemerintah lebih optimis (> 6.53%).
    """)
else:
    st.write("""
    Usulan Iuran 9% sudah **CUKUP** dan bahkan memberikan sedikit Surplus untuk membiayai manfaat 1.5%.
    Program akan berjalan sehat (Solven).
    """)