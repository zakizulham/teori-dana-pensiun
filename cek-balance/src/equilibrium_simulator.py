import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIG ---
st.set_page_config(page_title="Simulator Equilibrium Dana Pensiun", layout="wide")

# --- JUDUL & KONTEKS ---
st.title("⚖️ Simulator Keseimbangan Aktuaria (The Pricing Problem)")
st.markdown("""
Aplikasi ini memvisualisasikan **Prinsip Ekuivalensi**: *Nilai Aset harus sama dengan Nilai Kewajiban.*
Gunakan slider di bawah untuk mencari titik temu (Equilibrium) antara Iuran yang dibayar dan Manfaat yang dijanjikan.
""")

# --- PARAMETER FORENSIK (HARDCODED DARI ANALISA SEBELUMNYA) ---
# Kita kunci parameter ekonomi agar konsisten dengan 'Case Study' Slide 17
SALARY_INC_RATE = 0.0787   # 7.87% (High Salary Growth)
INVEST_RET_RATE = 0.0653   # 6.53% (Moderate Return)
DISCOUNT_RATE   = 0.057    # 5.7%
YEARS           = 32
START_WAGE      = 2_500_000

# Annuity Factor Implisit (Joint Life 50%) yang menghasilkan Liabilitas ~561 Juta
# Ini kita kunci agar simulasi fokus pada Trade-off Iuran vs Manfaat
IMPLIED_ANNUITY_FACTOR = 14.32 

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🎛️ Kendali Kebijakan")

st.sidebar.subheader("1. Sisi Aset (Pemasukan)")
contribution_rate = st.sidebar.slider(
    "Tingkat Iuran (% dari Gaji)", 
    min_value=1.0, 
    max_value=15.0, 
    value=3.0, 
    step=0.01,
    help="Berapa persen gaji yang disisihkan setiap bulan?"
) / 100

st.sidebar.divider()

st.sidebar.subheader("2. Sisi Liabilitas (Pengeluaran)")
accrual_rate = st.sidebar.slider(
    "Accrual Rate / Rumus Manfaat (%)", 
    min_value=0.5, 
    max_value=2.5, 
    value=1.0, 
    step=0.1,
    help="Berapa persen pengali manfaat? (Slide 17 = 1%, Slide 22 usul naik ke 1.5%)"
) / 100

# --- CALCULATION ENGINE ---
def calculate_actuarial_balance(cont_rate, acc_rate):
    # 1. Proyeksi Gaji & Aset
    curr_w = START_WAGE
    accum_asset = 0
    wages = []
    
    for t in range(YEARS):
        wages.append(curr_w)
        # Hitung iuran tahun ini
        annual_cont = curr_w * 12 * cont_rate
        # Kembangkan aset (Future Value)
        remaining_years = YEARS - 1 - t
        fv_cont = annual_cont * ((1 + INVEST_RET_RATE) ** remaining_years)
        accum_asset += fv_cont
        # Gaji naik
        curr_w *= (1 + SALARY_INC_RATE)
        
    # 2. Valuasi Liabilitas
    avg_wage = np.mean(wages)
    # Rumus Manfaat: Accrual Rate x Masa Kerja x Rata-rata Gaji
    annual_benefit = acc_rate * YEARS * avg_wage * 12
    # Present Value
    total_liability = annual_benefit * IMPLIED_ANNUITY_FACTOR
    
    return accum_asset, total_liability

# Run Calculation
asset, liability = calculate_actuarial_balance(contribution_rate, accrual_rate)
funding_ratio = (asset / liability) * 100 if liability > 0 else 0
gap = asset - liability

# Hitung "Fair Price" (Iuran yang SEHARUSNYA untuk manfaat yang dipilih)
# Asset(at X%) = Liability -> X = (Liability / Asset_at_1%) * 1%
asset_at_1_pct, _ = calculate_actuarial_balance(0.01, accrual_rate)
required_contribution = (liability / asset_at_1_pct) if asset_at_1_pct > 0 else 0

# --- DASHBOARD VISUALIZATION ---

# Row 1: The Big Warning
if funding_ratio < 100:
    st.error(f"⚠️ PERINGATAN: DANA PENSIUN PASTI BANGKRUT SECARA MATEMATIS! (Ratio: {funding_ratio:.1f}%)")
else:
    st.success(f"✅ AMAN: DANA PENSIUN SOLVEN (Ratio: {funding_ratio:.1f}%)")

# Row 2: Gauge & Metrics
col1, col2 = st.columns([1, 2])

with col1:
    # Gauge Chart untuk Funding Ratio
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = funding_ratio,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Funding Ratio (Kecukupan Dana)"},
        delta = {'reference': 100},
        gauge = {
            'axis': {'range': [None, 200]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 99.9], 'color': "lightpink"},
                {'range': [100, 200], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.subheader("Neraca Aktuaria")
    
    # Bar Chart Perbandingan
    fig_bar = go.Figure(data=[
        go.Bar(name='Aset (Uang Ada)', x=['Neraca'], y=[asset], marker_color='#2ecc71'),
        go.Bar(name='Liabilitas (Janji)', x=['Neraca'], y=[liability], marker_color='#e74c3c')
    ])
    fig_bar.update_layout(barmode='group', height=400, title="Aset vs Liabilitas")
    st.plotly_chart(fig_bar, use_container_width=True)

# Row 3: Detailed Metrics & Equilibrium Analysis
st.divider()
c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Total Aset", f"Rp {asset:,.0f}")
with c2:
    st.metric("Total Liabilitas", f"Rp {liability:,.0f}")
with c3:
    st.metric("Surplus / (Defisit)", f"Rp {gap:,.0f}", delta_color="normal")

st.divider()

# Row 4: Analisis Equilibrium (The Solution)
st.subheader("🔍 Analisa Titik Equilibrium (Solusi)")

st.markdown(f"""
Untuk membayar janji manfaat sebesar **{accrual_rate*100}%** (Accrual Rate),
secara matematika aktuaria dibutuhkan iuran sebesar:
""")

col_sol1, col_sol2 = st.columns(2)
with col_sol1:
    st.metric("Harga Wajar (Required Contribution)", f"{required_contribution:.2f}%")
with col_sol2:
    st.metric("Iuran Saat Ini", f"{contribution_rate*100:.2f}%", 
              delta=f"{(contribution_rate*100) - required_contribution:.2f}% Gap")

if contribution_rate * 100 < required_contribution:
    st.info(f"💡 **Insight:** Iuran Anda kurang **{required_contribution - (contribution_rate*100):.2f}%** untuk mencapai titik impas.")
else:
    st.success("💡 **Insight:** Iuran Anda sudah cukup untuk membiayai manfaat ini.")

# --- FOOTER ---
st.caption("Simulator ini menggunakan asumsi 'Negative Spread' (Gaji naik 7.8%, Investasi 6.5%) sesuai temuan forensik Slide 17.")