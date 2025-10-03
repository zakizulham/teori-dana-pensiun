# Kalkulator Iuran DPLK untuk Target Pensiun (IRR)

Repositori ini berisi analisis dan skrip kalkulator untuk menyelesaikan studi kasus dalam menentukan iuran bulanan Dana Pensiun Lembaga Keuangan (DPLK) yang diperlukan untuk mencapai target *Income Replacement Ratio* (IRR) sebesar 80%.

Kalkulator ini menyediakan estimasi yang komprehensif dengan memperhitungkan tiga sumber utama dana pensiun yang ada di Indonesia:
1.  **BPJS Ketenagakerjaan - Jaminan Hari Tua (JHT)**
2.  **BPJS Ketenagakerjaan - Jaminan Pensiun (JP)**
3.  **Uang Pesangon (sesuai UU Cipta Kerja / PP No. 35 Tahun 2021)**


## 🎯 Latar Belakang

Seorang pekerja ingin memastikan bahwa saat pensiun nanti, ia akan menerima penghasilan bulanan setidaknya 80% dari gaji terakhirnya. Dengan memperhitungkan semua manfaat pensiun yang sudah dijamin oleh pemerintah dan perusahaan, proyek ini bertujuan untuk menghitung berapa besar selisih (*gap*) yang masih ada dan berapa iuran DPLK bulanan yang diperlukan untuk menutup selisih tersebut.

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
1.  **Proyeksi Gaji & Target Pensiun**: Menghitung gaji pada usia pensiun dan menentukan target penghasilan pensiun bulanan.
2.  **Estimasi Manfaat JHT & Pesangon**: Menghitung total akumulasi dana *lump sum* dari Jaminan Hari Tua (JHT) dan total Uang Pesangon (mencakup UP, UPMK, dan UPH) pada usia pensiun 55.
3.  **Estimasi Manfaat Jaminan Pensiun (JP)**:
    * Menghitung estimasi manfaat pensiun bulanan yang akan diterima dari JP mulai usia 60 tahun.
    * Menghitung **Nilai Sekarang (Present Value)** dari seluruh aliran manfaat JP tersebut, ditarik mundur ke titik usia 55. Ini menghasilkan nilai *lump sum* yang setara.
4.  **Agregasi Dana Pensiun**: Menjumlahkan seluruh sumber dana yang ada (JHT, Pesangon, dan PV Manfaat JP) untuk mendapatkan total dana *lump sum* yang setara di usia 55.
5.  **Konversi ke Anuitas & Perhitungan Gap**: Mengonversi total dana *lump sum* menjadi estimasi manfaat pensiun bulanan seumur hidup, lalu membandingkannya dengan target untuk menemukan selisih (*gap*).
6.  **Perhitungan Iuran DPLK**: Menentukan iuran DPLK bulanan yang diperlukan untuk menutupi *gap* tersebut.

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
├── kalkulator.py          # Versi awal (tanpa JP)
├── kalkulator2.py         # Versi final (dengan JP & pesangon detail)
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
    python kalkulator2.py
    ```
    Hasil perhitungan akan ditampilkan langsung di terminal Anda.

### Kustomisasi Skenario
Anda dapat dengan mudah mengubah asumsi perhitungan (seperti gender, usia, gaji awal, atau imbal hasil) dengan mengedit variabel yang ada di bagian atas file `kalkulator2.py` pada **TAHAP 1: INISIALISASI & ASUMSI**.

```python
# Contoh kustomisasi di kalkulator.py
gender = 'f'  # Ubah ke 'f' untuk subjek wanita
gaji_awal_bulanan = 10_000_000  # Ubah gaji awal
kenaikan_gaji_pa = 0.06 # Ubah asumsi kenaikan gaji
```

---

### 📄 Panduan Implementasi di Microsoft Excel

Selain menggunakan skrip Python, seluruh logika kalkulator ini (termasuk perhitungan JP dan pesangon detail) juga dapat direplikasi sepenuhnya di Microsoft Excel. Pendekatan ini cocok bagi pengguna yang lebih menyukai antarmuka visual. Panduan ini memecah kalkulator ke dalam tiga *sheet*: `Dashboard`, `Proyeksi Tahunan`, dan `Referensi`.

Panduan ini memecah kalkulator ke dalam tiga *sheet* yang saling berhubungan:

1.  **`Dashboard`**
    -   **Tujuan**: Menjadi pusat kendali di mana semua variabel input (seperti usia, gaji awal, imbal hasil, dll.) ditempatkan. Mengubah nilai di *sheet* ini akan secara otomatis memperbarui seluruh perhitungan. Menjadi dasbor akhir yang merangkum semua hasil ke permukaan Hasil & Solusi yang terdiri dari Manfaat Jaminan Penisun, Total Dana Lump Sum, Estimasi Kekurangan, dan **Iuran DPLK bulanan yang direkomendasikan**.

2.  **`Proyeksi Tahunan`**
    -   **Tujuan**: Membuat tabel simulasi tahun-demi-tahun untuk menghitung akumulasi dana JHT. *Sheet* ini memproyeksikan pertumbuhan gaji, iuran tahunan, dan imbal hasil investasi pada saldo JHT dari usia mulai hingga usia pensiun. Selain itu, di *Sheet* ini juga dilakukan perhitungan aktuaria untuk menemukan **Faktor Anuitas Hidup ($\ddot{a}_x$)**. Faktor ini adalah kunci untuk mengonversi sejumlah dana *lump sum* menjadi estimasi penghasilan pensiun bulanan seumur hidup.

4.  **`Referensi`**
    -   **Tujuan**: Mengikuti Standar PP No.35 Tahun 2021 Pasal 40 ayat 2 dan Pasal 40 ayat 3 untuk perhitungan detail terkait PHK akibat usia pensiun.

---

## 🤝 Kontribusi

Kontribusi dalam bentuk *pull request*, laporan *issue*, atau saran sangat kami hargai.

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).