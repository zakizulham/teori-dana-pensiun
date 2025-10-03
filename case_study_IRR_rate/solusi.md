# Solusi Kalkulator
Di bawah ini adalah output solusi masing-masing kalkulator agar dapat dibaca tiap saat tanpa perlu menjalankan ulang file python tersebut.

## Solusi Kalkulator 1

```markdown
$ python kalkulator.py 
✅ Berhasil memuat tabel mortalita: data/tmi_4_m.csv

--- MULAI KALKULASI STUDI KASUS IRR ---

[1] Proyeksi & Target Pensiun (Usia 55)
    - Gaji terakhir per bulan : Rp 16,631,425
    - Target pensiun per bulan: Rp 13,305,140

[2] Estimasi Manfaat Pensiun di Usia 55 (Lump Sum)
    - Akumulasi Dana JHT      : Rp 173,807,143
    - Uang Pesangon (UUCK)    : Rp 149,682,829
    -------------------------------------------------- +
    - Total Dana Siap Pakai   : Rp 323,489,972

[3] Konversi Dana ke Pensiun Bulanan Seumur Hidup
    - Faktor Anuitas (ä_55) : 13.3752
    - Estimasi Pensiun Bulanan: Rp 2,015,478

[4] Kebutuhan & Kekurangan Pensiun
    - Target Pensiun Bulanan  : Rp 13,305,140
    - Manfaat yang Ada        : Rp 2,015,478
    -------------------------------------------------- -
    - Kekurangan (GAP)        : Rp 11,289,662

[5] Solusi: Iuran DPLK
    - Dana DPLK harus terkumpul: Rp 1,812,022,755
    - Persentase dari gaji awal: 78.95%

==============================================================================
✅ IURAN DPLK BULANAN YANG DIPERLUKAN: Rp 6,315,607
==============================================================================
```

## Solusi Kalkulator 2

```markdown
$ python kalkulator2.py 
✅ Berhasil memuat tabel mortalita: data/tmi_4_m.csv

--- KALKULATOR PENSIUN V2 (TERMASUK JAMINAN PENSIUN) ---

[1] Proyeksi & Target Pensiun (Usia 55)
    - Gaji terakhir per bulan : Rp 16,631,425
    - Target pensiun per bulan: Rp 13,305,140

[2] Estimasi Manfaat Pensiun di Usia 55 (Lump Sum Equivalent)
    - Akumulasi Dana JHT      : Rp 173,807,143
    - Uang Pesangon (UUCK)    : Rp 415,993,529
    - PV Manfaat JP di Usia 55: Rp 540,012,874
    -------------------------------------------------- +
    - Total Dana Siap Pakai   : Rp 1,129,813,547

[3] Konversi Dana ke Pensiun Bulanan Seumur Hidup
    - Faktor Anuitas (ä_55) : 13.3752
    - Faktor Anuitas (ä_60) : 12.5663
    - Estimasi Pensiun Bulanan: Rp 7,039,212

[4] Kebutuhan & Kekurangan Pensiun
    - Target Pensiun Bulanan  : Rp 13,305,140
    - Manfaat yang Ada        : Rp 7,039,212
    -------------------------------------------------- -
    - Kekurangan (GAP)        : Rp 6,265,928

[5] Solusi: Iuran DPLK
    - Dana DPLK harus terkumpul: Rp 1,005,699,180
    - Persentase dari gaji awal: 43.82%

==============================================================================
✅ IURAN DPLK BULANAN (DENGAN JP): Rp 3,505,254
==============================================================================
```