import pandas as pd
import numpy as np

def is_id_col(col_name):
    """Cek apakah kolom adalah ID berdasarkan nama."""
    cl = col_name.lower().replace('_', '').replace(' ', '')
    return cl in ('id', 'patientid') or cl.endswith('id')

def detect_column_types(df):
    """Kembalikan pengelompokan kolom numerik, kategorikal, datetime, dan semua (tanpa ID)."""
    numeric, categorical, datetime_cols = [], [], []

    for col in df.columns:
        if is_id_col(col):
            continue

        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], errors='coerce')
                if parsed.notna().sum() > len(df) * 0.5:
                    datetime_cols.append(col)
                    continue
            except Exception:
                pass
            categorical.append(col)
            continue

        unique_count = df[col].nunique()
        ratio = unique_count / len(df)

        # ≤15 nilai unik DAN muncul sangat jarang (<5%) → anggap kategorikal
        if unique_count <= 15 and ratio < 0.05:
            categorical.append(col)
        else:
            numeric.append(col)

    safe_all = [c for c in df.columns if not is_id_col(c)]

    return {
        'numeric': numeric,
        'categorical': categorical,
        'datetime': datetime_cols,
        'all': safe_all
    }

def generate_insights(df, ct):
    """Buat daftar insight berdasarkan data dan tipe kolom."""
    insights = []
    num = ct['numeric']
    cat = ct['categorical']

    insights.append({
        'type': 'info', 'icon': '📊', 'title': 'Ringkasan Dataset',
        'text': f"Dataset memiliki <b>{len(df):,} baris</b> dan <b>{len(df.columns)} kolom</b>. "
                f"{len(num)} numerik, {len(cat)} kategorikal."
    })

    miss = df.isnull().sum()
    miss_cols = miss[miss > 0]
    if len(miss_cols):
        txt = ', '.join(f"<b>{c}</b> ({v})" for c, v in miss_cols.items())
        insights.append({'type': 'warning', 'icon': '⚠️', 'title': 'Data Kosong', 'text': f"Kolom kosong: {txt}."})
    else:
        insights.append({'type': 'success', 'icon': '✅', 'title': 'Data Lengkap', 'text': 'Tidak ada missing values.'})

    for col in num[:3]:
        mv, mdv, sv, skv = df[col].mean(), df[col].median(), df[col].std(), df[col].skew()
        skd = ("distribusi <b>simetris</b>" if abs(skv) < 0.5
               else f"condong ke <b>kanan</b> (skew +{skv:.2f})" if skv > 0
               else f"condong ke <b>kiri</b> (skew {skv:.2f})")
        outn = " Kemungkinan ada <b>outlier</b>." if abs(mv - mdv) / (abs(mdv) + 1e-9) * 100 > 10 else ""
        insights.append({
            'type': 'stat', 'icon': '📈', 'title': f'Statistik: {col}',
            'text': f"Mean <b>{mv:.2f}</b>, median <b>{mdv:.2f}</b>, std <b>{sv:.2f}</b>. {skd}.{outn}"
        })

    if cat and num:
        try:
            gs = df.groupby(cat[0])[num[0]].mean().sort_values(ascending=False)
            if len(gs) >= 2:
                insights.append({
                    'type': 'compare', 'icon': '🔍',
                    'title': f'Perbandingan: {cat[0]} vs {num[0]}',
                    'text': f"Kelompok <b>{gs.index[0]}</b> tertinggi (<b>{gs.iloc[0]:.2f}</b>), "
                            f"<b>{gs.index[-1]}</b> terendah (<b>{gs.iloc[-1]:.2f}</b>)."
                })
        except Exception:
            pass

    if len(num) >= 2:
        try:
            cm = df[num].corr().abs()
            np.fill_diagonal(cm.values, 0)
            pair = cm.unstack().idxmax()
            cv = df[pair[0]].corr(df[pair[1]])
            d = "positif" if cv > 0 else "negatif"
            s = "sangat kuat" if abs(cv) > 0.8 else "kuat" if abs(cv) > 0.6 else "sedang" if abs(cv) > 0.3 else "lemah"
            insights.append({
                'type': 'correlation', 'icon': '🔗', 'title': 'Korelasi Terkuat',
                'text': f"<b>{pair[0]}</b> dan <b>{pair[1]}</b> berkorelasi <b>{d} {s}</b> (r={cv:.3f})."
            })
        except Exception:
            pass

    for col in num[:2]:
        try:
            q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            iqr = q3 - q1
            n_out = int(((df[col] < q1 - 1.5 * iqr) | (df[col] > q3 + 1.5 * iqr)).sum())
            pct = n_out / len(df) * 100
            if pct > 1:
                insights.append({
                    'type': 'outlier', 'icon': '🚨', 'title': f'Outlier: {col}',
                    'text': f"<b>{n_out} data ({pct:.1f}%)</b> di luar [{q1 - 1.5 * iqr:.2f}, {q3 + 1.5 * iqr:.2f}]."
                })
        except Exception:
            pass

    return insights