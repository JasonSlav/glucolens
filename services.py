import pandas as pd
import numpy as np

class DataService:
    @staticmethod
    def is_id_col(col_name):
        """
        Mendeteksi apakah sebuah kolom kemungkinan besar adalah ID (Patient ID, No, dsb).
        Biasanya kolom ini tidak berguna untuk visualisasi statistik.
        """
        cl = str(col_name).lower().replace('_', '').replace(' ', '')
        return cl in ('id', 'patientid', 'no', 'index') or cl.endswith('id')

    @classmethod
    def detect_column_types(cls, df):
        """
        Secara otomatis mengklasifikasikan kolom menjadi Numerik, Kategorikal, atau Datetime.
        Menggunakan logika cerdas untuk membedakan angka kontinu dan kategori (misal: Skala 1-5).
        """
        numeric, categorical, datetime_cols = [], [], []
        
        for col in df.columns:
            if cls.is_id_col(col):
                continue
            
            # 1. Cek potensi Datetime
            if df[col].dtype == object or str(df[col].dtype).startswith('datetime'):
                try:
                    # Coba parsing, jika > 50% berhasil, anggap datetime
                    parsed = pd.to_datetime(df[col], errors='coerce')
                    if parsed.notna().sum() > len(df) * 0.5:
                        datetime_cols.append(col)
                        continue
                except:
                    pass
            
            # 2. Cek Numerik vs Kategorikal
            if pd.api.types.is_numeric_dtype(df[col]):
                unique_count = df[col].nunique()
                ratio = unique_count / len(df)
                
                # Jika angka pilihannya sedikit (misal: status 0/1 atau kategori 1-3),
                # masukkan ke kategori, bukan numerik kontinu.
                if unique_count <= 15 and ratio < 0.05:
                    categorical.append(col)
                else:
                    numeric.append(col)
            else:
                categorical.append(col)
                
        return {
            'numeric': numeric,
            'categorical': categorical,
            'datetime': datetime_cols,
            'all': [c for c in df.columns if not cls.is_id_col(c)]
        }

    @staticmethod
    def generate_insights(df, ct):
        """
        Menghasilkan ringkasan analisis otomatis (insights) berdasarkan data yang diupload.
        """
        insights = []
        num_cols = ct['numeric']
        cat_cols = ct['categorical']

        # 1. Insight: Ringkasan Ukuran Dataset
        insights.append({
            'type': 'info', 'icon': '📊', 'title': 'Profil Dataset',
            'text': f"Dataset ini memiliki <b>{len(df):,} baris</b> dengan <b>{len(num_cols)} variabel angka</b> dan <b>{len(cat_cols)} kategori</b>."
        })

        # 2. Insight: Pengecekan Data Kosong (Missing Values)
        missing = df.isnull().sum()
        missing_total = missing.sum()
        if missing_total > 0:
            bad_cols = missing[missing > 0].index.tolist()[:3]
            text = f"Ditemukan <b>{missing_total} data kosong</b>. Perhatian khusus pada: {', '.join(bad_cols)}."
            insights.append({'type': 'warning', 'icon': '⚠️', 'title': 'Data Tidak Lengkap', 'text': text})
        else:
            insights.append({'type': 'success', 'icon': '✅', 'title': 'Kualitas Data', 'text': 'Data bersih! Tidak ditemukan nilai kosong.'})

        # 3. Insight: Statistik Deskriptif (hanya untuk 2 kolom numerik pertama)
        for col in num_cols[:2]:
            mean_val = df[col].mean()
            med_val = df[col].median()
            skew = "condong ke atas" if mean_val > med_val else "cukup seimbang"
            insights.append({
                'type': 'stat', 'icon': '📈', 'title': f'Analisis {col}',
                'text': f"Rata-rata <b>{mean_val:.2f}</b> dengan titik tengah <b>{med_val:.2f}</b>. Distribusi terlihat {skew}."
            })

        # 4. Insight: Korelasi (jika ada minimal 2 kolom numerik)
        if len(num_cols) >= 2:
            try:
                corr_matrix = df[num_cols].corr().abs()
                # Cari pasangan korelasi tertinggi (selain dirinya sendiri)
                np.fill_diagonal(corr_matrix.values, 0)
                c_max = corr_matrix.unstack().idxmax()
                val_max = df[c_max[0]].corr(df[c_max[1]])
                
                if abs(val_max) > 0.5:
                    strength = "kuat" if abs(val_max) > 0.7 else "sedang"
                    insights.append({
                        'type': 'correlation', 'icon': '🔗', 'title': 'Hubungan Antar Data',
                        'text': f"Variabel <b>{c_max[0]}</b> dan <b>{c_max[1]}</b> memiliki hubungan yang <b>{strength}</b> ({val_max:.2f})."
                    })
            except:
                pass

        return insights