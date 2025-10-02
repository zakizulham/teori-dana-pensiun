# Kalkulator Iuran DPLK untuk Target Pensiun (IRR)

Repositori ini berisi analisis dan skrip kalkulator untuk menyelesaikan studi kasus dalam menentukan iuran bulanan Dana Pensiun Lembaga Keuangan (DPLK) yang diperlukan untuk mencapai target *Income Replacement Ratio* (IRR) sebesar 80%.

## 🎯 Latar Belakang

Seorang pekerja ingin memastikan bahwa saat pensiun nanti, ia akan menerima penghasilan bulanan setidaknya 80% dari gaji terakhirnya. Penghasilan pensiun ini akan berasal dari program wajib pemerintah (BPJS Ketenagakerjaan) dan kompensasi dari perusahaan (UUCK), namun kemungkinan besar masih ada selisih (gap) yang perlu ditutupi melalui program pensiun sukarela seperti DPLK.

Proyek ini bertujuan untuk menghitung berapa besar iuran bulanan yang harus disisihkan ke dalam program DPLK untuk menutupi selisih tersebut.

## 📝 Studi Kasus

### Skenario
Tentukan iuran bulanan DPLK yang diperlukan oleh seorang karyawan untuk mencapai IRR 80%, dengan mempertimbangkan manfaat yang sudah ada dari program berikut:
1.  **BPJS Ketenagakerjaan** (Jaminan Hari Tua & Jaminan Pensiun)
2.  **Uang Pesangon (UU Cipta Kerja)**

### Asumsi
-   **Usia Mulai Bekerja (Analisis)**: 40 tahun
-   **Usia Pensiun Normal**: 55 tahun
-   **Gaji Awal (Usia 40)**: Rp 8.000.000 / bulan
-   **Kenaikan Gaji Tahunan**: 5%
-   **Imbal Hasil Investasi (DPLK & JHT)**: 6% per tahun
-   **Target IRR**: 80% dari gaji terakhir
-   **Pajak & Biaya**: Diabaikan untuk simplifikasi

### Data Aktuaria
Perhitungan anuitas untuk manfaat pensiun bulanan mengacu pada tabel mortalita yang tersedia, seperti TMI 4, GAM 71, atau GAM 83, yang dibedakan berdasarkan jenis kelamin (pria/wanita).

---

##  metodologi Perhitungan

Perhitungan dibagi menjadi beberapa tahap utama:
1.  **Proyeksi Gaji & Target Pensiun**: Menghitung gaji pada usia pensiun dan menentukan target penghasilan pensiun bulanan (80% dari gaji terakhir).
2.  **Estimasi Manfaat yang Ada**: Menghitung total akumulasi dana *lump sum* dari Jaminan Hari Tua (JHT) dan Uang Pesangon (UUCK) pada usia pensiun.
3.  **Konversi ke Anuitas Hidup**: Mengonversi total dana *lump sum* tersebut menjadi estimasi manfaat pensiun bulanan seumur hidup menggunakan tabel mortalita dan asumsi imbal hasil.
4.  **Perhitungan Kekurangan (Gap)**: Membandingkan target pensiun bulanan dengan estimasi manfaat yang sudah ada untuk menemukan selisihnya.
5.  **Perhitungan Iuran DPLK**: Menentukan berapa dana yang harus terakumulasi di DPLK untuk menutupi *gap*, lalu menghitung iuran bulanan yang diperlukan untuk mencapai jumlah tersebut.

---

## 📂 Struktur Proyek

Struktur file dan folder dalam repositori ini adalah sebagai berikut:

```
.
├── data/
│   ├── gam_71_f.csv
│   ├── gam_71_m.csv
│   ├── gam_83_f.csv
│   ├── gam_83_m.csv
│   ├── tmi_4_f.csv
│   └── tmi_4_m.csv
├── kalkulator.py
└── README.md
```

## 🚀 Cara Menjalankan Kalkulator (Reproducibility)

Untuk menjalankan kalkulator dan mereproduksi hasil perhitungan, ikuti langkah-langkah berikut.

### Prasyarat
-   Python 3.8 atau versi lebih baru.
-   Git untuk mengkloning repositori.

### Langkah-langkah Instalasi & Eksekusi

1.  **Clone Repositori**
    Buka terminal atau command prompt Anda dan jalankan perintah berikut:
    ```bash
    git clone [https://github.com/zakizulham/teori-dana-pensiun.git](https://github.com/zakizulham/teori-dana-pensiun.git)
    cd teori-dana-pensiun/case_study_IRR_rate
    ```

2.  **Buat dan Aktifkan Virtual Environment (Sangat Disarankan)**
    Membuat lingkungan virtual akan mengisolasi dependensi proyek Anda.
    ```bash
    # Membuat virtual environment
    python -m venv .venv

    # Mengaktifkan di Windows
    .\.venv\Scripts\activate

    # Mengaktifkan di macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependensi yang Dibutuhkan**
    Install library Python yang diperlukan oleh skrip.
    ```bash
    pip install pandas numpy-financial
    ```

4.  **Jalankan Skrip Kalkulator**
    Setelah dependensi terinstall, jalankan skrip utama:
    ```bash
    python kalkulator.py
    ```
    Hasil perhitungan akan ditampilkan langsung di terminal Anda.

### Kustomisasi Skenario
Anda dapat dengan mudah mengubah asumsi perhitungan (seperti gender, usia, gaji awal, atau imbal hasil) dengan mengedit variabel yang ada di bagian atas file `kalkulator.py` pada **TAHAP 1: INISIALISASI & ASUMSI**.

```python
# Contoh kustomisasi di kalkulator.py
gender = 'f'  # Ubah ke 'f' untuk subjek wanita
gaji_awal_bulanan = 10_000_000  # Ubah gaji awal
kenaikan_gaji_pa = 0.06 # Ubah asumsi kenaikan gaji
```

---

### 📄 Panduan Implementasi di Microsoft Excel

Selain menggunakan skrip Python, seluruh logika kalkulator ini juga dapat direplikasi sepenuhnya di Microsoft Excel. Pendekatan ini cocok bagi pengguna yang lebih menyukai antarmuka visual dan ingin melihat perubahan perhitungan secara *real-time* saat asumsi diubah.

Panduan ini memecah kalkulator ke dalam empat *sheet* yang saling berhubungan:

1.  **`Asumsi`**
    -   **Tujuan**: Menjadi pusat kendali di mana semua variabel input (seperti usia, gaji awal, imbal hasil, dll.) ditempatkan. Mengubah nilai di *sheet* ini akan secara otomatis memperbarui seluruh perhitungan.

2.  **`Proyeksi Tahunan`**
    -   **Tujuan**: Membuat tabel simulasi tahun-demi-tahun untuk menghitung akumulasi dana JHT. *Sheet* ini memproyeksikan pertumbuhan gaji, iuran tahunan, dan imbal hasil investasi pada saldo JHT dari usia mulai hingga usia pensiun.

3.  **`Tabel Mortalita`**
    -   **Tujuan**: Melakukan perhitungan aktuaria untuk menemukan **Faktor Anuitas Hidup ($\ddot{a}_x$)**. Faktor ini adalah kunci untuk mengonversi sejumlah dana *lump sum* menjadi estimasi penghasilan pensiun bulanan seumur hidup.

4.  **`Hasil & Solusi`**
    -   **Tujuan**: Menjadi dasbor akhir yang merangkum semua hasil. *Sheet* ini mengambil data dari tiga *sheet* lainnya untuk menghitung total dana yang ada, membandingkannya dengan target pensiun, menemukan kekurangan (*gap*), dan akhirnya menghitung **iuran DPLK bulanan yang direkomendasikan**.

---

## 🤝 Kontribusi

Kontribusi dalam bentuk *pull request*, laporan *issue*, atau saran sangat kami hargai.

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).