# GlucoLens — Dashboard Visualisasi Data Diabetes

**GlucoLens** adalah aplikasi web interaktif untuk mengeksplorasi dan memvisualisasikan dataset diabetes secara instan.  
Cukup unggah file CSV, dan dashboard akan menampilkan ringkasan analisis otomatis serta berbagai jenis grafik yang dapat disesuaikan.

![GlucoLens Screenshot](https://via.placeholder.com/800x400?text=GlucoLens+Dashboard)  
*(screenshot akan ditambahkan nanti)*

---

## ✨ Fitur Utama

- **Upload CSV** – Dukungan *drag-and-drop* file diabetes. (Sementara ini masih dites dengan dataset [🩸Diabetes Health Dataset Analysis🩸](https://www.kaggle.com/datasets/rabieelkharoua/diabetes-health-dataset-analysis?resource=download))
- **Deteksi Tipe Kolom Otomatis** – Numerik, kategorikal, datetime langsung dikenali.
- **Ringkasan Analisis (Insight)** – Statistik deskriptif, korelasi, outlier, dan perbandingan otomatis.
- **8+ Jenis Visualisasi** – Bar, Pie, Heatmap, Box, Scatter, Histogram, Violin, Line, Time Series.
- **Filter Variabel Cerdas** – Dropdown hanya menampilkan kolom yang kompatibel dengan chart.
- **Mode Eksplorasi** – Bebaskan semua tipe kolom untuk eksperimen.
- **Tema Gelap** – Tampilan modern dan nyaman di mata.
- **Responsif** – Dapat digunakan di desktop maupun tablet.

---

## 🛠️ Teknologi

| Bagian | Teknologi |
|--------|-----------|
| **Backend** | Flask, Pandas, Plotly, NumPy, PyArrow |
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla), Plotly.js |
| **Deployment** | PythonAnywhere (backend), Cloudflare Pages (frontend + proxy) |

---

## 🧩 Arsitektur

```
Pengguna → Cloudflare Pages (index.html + _middleware.js)
                │
                ├─ /              → file statis (frontend)
                └─ /upload, dll. → diteruskan ke PythonAnywhere (Flask)
                                        │
                                        └─ Proses CSV, buat chart, kirim JSON
```

Semua berjalan dalam satu domain Cloudflare Pages, tanpa masalah CORS.

---

## 🚀 Cara Menjalankan di Lokal

1. **Clone repositori**
   ```bash
   git clone https://github.com/username/glucolens.git
   cd glucolens
   ```

2. **Buat virtual environment** (opsional tapi disarankan)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Instal dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan server Flask**
   ```bash
   python app.py
   ```

5. **Buka di browser**
   ```
   http://localhost:5000
   ```

---
## 📁 Struktur Proyek

```
glucolens/
├── app.py                    # Flask entry point
├── requirements.txt          # Daftar pustaka Python
├── index.html                # Frontend (salinan dari templates/)
├── functions/
│   └── _middleware.js        # Proxy Cloudflare Pages → backend
├── utils/
│   ├── __init__.py
│   ├── data_processing.py    # Deteksi tipe kolom & insight
│   └── themes.py             # Tema gelap Plotly
├── charts/
│   ├── __init__.py
│   └── builders.py           # Semua fungsi pembuat chart
└── templates/
    └── index.html            # Versi asli (digunakan Flask)
```

---

## 📊 Penggunaan

1. Buka aplikasi, klik atau *drag* file CSV ke area upload.
2. Setelah dataset dimuat, pilih jenis visualisasi (Bar, Pie, dll.).
3. Pilih kolom yang diinginkan (X, Y, Warna).  
   ➤ Dropdown otomatis terfilter sesuai chart.
4. Klik **Visualisasi Data**.
5. Grafik muncul di panel kanan.  
   ➤ Gunakan *zoom*, *pan*, atau *reset axes* sesuai kebutuhan.

---

## 📝 Contoh Dataset

Dua baris pertama contoh dataset diabetes (format CSV):

```
PatientID,Age,Gender,Ethnicity,...
6000,44,0,1,...
6001,51,1,0,...
```

Kolom mencakup demografi, riwayat kesehatan, hasil lab, dan diagnosis.

---

## ⚠️ Batasan

- **Penyimpanan gratis PythonAnywhere** tidak *persistent* – file Parquet di folder `temp_data/` akan hilang setelah periode tidak aktif.
- **Solusi jangka panjang**: Ganti penyimpanan ke Cloudflare R2 (gratis 10 GB) – *akan ditambahkan*.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE) – bebas digunakan, dimodifikasi, dan disebarluaskan.

---

## 💬 Umpan Balik

Jika Anda menemukan masalah atau memiliki saran, silakan buka [Issue](https://github.com/username/glucolens/issues) di repositori ini.
