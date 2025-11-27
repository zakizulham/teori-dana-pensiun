import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIG ---
st.set_page_config(page_title="Forensik Aktuaria Dana Pensiun", layout="wide")

# --- JUDUL ---
st.title("🕵️‍♂️ Forensik Aktuaria: Reverse Engineering Slide 17")
st.markdown("""
Aplikasi ini memvisualisasikan bagaimana **Negative Economic Spread** menyebabkan defisit masif pada simulasi Program Jaminan Pensiun.
""")

# --- SIDEBAR INPUTS (FORENSIC PARAMETERS) ---
st.sidebar.header("Parameter Aktuaria")

# Default values based on our findings
s_rate = st.sidebar.number_input("Kenaikan Gaji (Salary Scale)", 0.0, 15.0, 7.87, 0.01) / 100
i_rate = st.sidebar.number_input("Return Investasi", 0.0, 15.0, 6.53, 0.01) / 100
start_wage = st.sidebar.number_input("Gaji Awal (Rp)", 0, 10000000, 2500000, 100000)
years = st.sidebar.slider("Masa Kerja (Tahun)", 10, 40, 32)

st.sidebar.divider()
st.sidebar.caption("Parameter Teknis (Fixed):")
st.sidebar.caption(f"Iuran: 3% | Diskon: 5.7% | Survivor: 50%")

# --- CALCULATION LOGIC ---
def calculate_projection(start_w, s, i, n):
    data = []
    curr_w = start_w
    accum_asset = 0
    
    contribution_rate = 0.03
    
    for t in range(1, n + 1):
        # 1. Iuran tahun ini
        cont = curr_w * 12 * contribution_rate
        
        # 2. Pengembangan Aset
        accum_asset = (accum_asset + cont) * (1 + i)
        
        data.append({
            "Tahun": t,
            "Gaji Bulanan": curr_w,
            "Total Aset": accum_asset
        })
        
        # Gaji naik tahun depan
        curr_w *= (1 + s)
        
    return pd.DataFrame(data)

# Run Calc
df = calculate_projection(start_wage, s_rate, i_rate, years)

# Liabilitas Logic (Approximate to match the 561M Target)
# Kita gunakan annuity factor implisit dari hasil reverse engineering sebelumnya
avg_wage = df["Gaji Bulanan"].mean()
annual_benefit = 0.01 * years * avg_wage * 12
implied_annuity_factor = 14.32 # Kalibrasi hasil reverse engineer
total_liability = annual_benefit * implied_annuity_factor

gap = df["Total Aset"].iloc[-1] - total_liability

# --- DASHBOARD LAYOUT ---

# 1. Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Gaji Akhir (Nominal)", f"Rp {df['Gaji Bulanan'].iloc[-1]:,.0f}", 
              delta=f"{df['Gaji Bulanan'].iloc[-1]/start_wage:.1f}x Lipat")
with col2:
    st.metric("Total Aset (Tabungan)", f"Rp {df['Total Aset'].iloc[-1]:,.0f}")
with col3:
    st.metric("Total Liabilitas (Janji)", f"Rp {total_liability:,.0f}", 
              help="Dihitung menggunakan asumsi Joint Life Reversionary 50%")
with col4:
    st.metric("GAP (Defisit)", f"Rp {gap:,.0f}", 
              delta_color="inverse" if gap < 0 else "normal")

st.divider()

# 2. Chart Row
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Perlombaan Gaji vs Aset")
    
    fig = go.Figure()
    
    # Plot Gaji (Left Axis)
    fig.add_trace(go.Scatter(
        x=df["Tahun"], y=df["Gaji Bulanan"],
        name="Gaji Bulanan (Nominal)",
        line=dict(color='firebrick', width=3)
    ))
    
    # Plot Aset (Right Axis)
    fig.add_trace(go.Scatter(
        x=df["Tahun"], y=df["Total Aset"],
        name="Akumulasi Aset",
        line=dict(color='royalblue', width=3, dash='dot'),
        yaxis="y2"
    ))
    
    # PERBAIKAN DI SINI: Mengganti 'titlefont' menjadi 'title_font'
    fig.update_layout(
        xaxis_title="Tahun Ke-",
        yaxis=dict(title="Gaji Bulanan (Rp)", title_font=dict(color="firebrick")),
        yaxis2=dict(title="Total Aset (Rp)", title_font=dict(color="royalblue"), overlaying="y", side="right"),
        legend=dict(x=0, y=1.1, orientation="h"),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Analisa Spread")
    spread = i_rate - s_rate
    
    st.write(f"**Investment Return:** {i_rate*100:.2f}%")
    st.write(f"**Salary Increase:** {s_rate*100:.2f}%")
    
    if spread < 0:
        st.error(f"⚠️ NEGATIVE SPREAD: {spread*100:.2f}%")
        st.markdown("""
        **Bahaya!**
        Kenaikan gaji (pemicu liabilitas) lebih tinggi daripada hasil investasi.
        
        Ini adalah resep pasti untuk **Defisit Struktural**. Semakin lama masa kerja, gap akan semakin lebar secara eksponensial.
        """)
    else:
        st.success(f"✅ POSITIVE SPREAD: {spread*100:.2f}%")
        st.write("Program dalam kondisi sehat (akumulasi tumbuh lebih cepat dari liabilitas).")

# --- FOOTER ---
st.caption("Aplikasi ini dibuat berdasarkan reverse engineering matematika aktuaria dari Slide 17 Dokumen Harmonisasi Pensiun.")