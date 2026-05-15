import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def prepare_numeric_df(df, cols):
    """Ubah string angka dengan koma menjadi float, buang NaN/Inf."""
    dc = df.copy()
    for col in cols:
        if col and col in dc.columns:
            dc[col] = pd.to_numeric(
                dc[col].astype(str).str.replace(',', '.', regex=False).str.strip(),
                errors='coerce'
            )
    dc = dc.replace([np.inf, -np.inf], np.nan)
    dc = dc.dropna(subset=[c for c in cols if c])
    return dc


def build_bar_chart(dc, x_col, y_col, color_col):
    if y_col:
        if pd.api.types.is_numeric_dtype(dc[y_col]) and dc[y_col].nunique() > 5:
            agg = dc.groupby(x_col)[y_col].mean().reset_index()
            agg[x_col] = agg[x_col].astype(str)
            fig = px.bar(agg, x=x_col, y=y_col, color=color_col if color_col in agg.columns else None,
                         title=f'Rata-rata {y_col} per {x_col}', text_auto='.2f')
        else:
            counts = dc.groupby([x_col, y_col]).size().reset_index(name='Jumlah')
            counts[x_col] = counts[x_col].astype(str)
            counts[y_col] = counts[y_col].astype(str)
            fig = px.bar(counts, x=x_col, y='Jumlah', color=y_col, barmode='group',
                         title=f'Distribusi {x_col} berdasarkan {y_col}', text_auto=True)
    else:
        counts = dc[x_col].value_counts().reset_index()
        counts.columns = [x_col, 'Jumlah']
        counts[x_col] = counts[x_col].astype(str)
        fig = px.bar(counts, x=x_col, y='Jumlah',
                     color=color_col if color_col in counts.columns else None,
                     title=f'Distribusi {x_col}', text_auto=True)
    return fig, None


def build_histogram(dc, x_col, y_col, color_col):
    dc = prepare_numeric_df(dc, [x_col])
    if dc.empty:
        return None, "Kolom X kosong setelah dibersihkan."

    q99 = dc[x_col].quantile(0.99)
    dc = dc[dc[x_col] <= q99]

    fig = go.Figure()

    if color_col and color_col in dc.columns:
        # Batasi maksimal 20 grup agar performa tetap baik
        grouped = dc.groupby(color_col)
        n_groups = len(grouped)
        if n_groups > 20:
            # Ambil 20 grup terbesar saja
            top_groups = dc[color_col].value_counts().head(20).index
            grouped = {g: dc[dc[color_col] == g] for g in top_groups}
            # Konversi ke list of tuples agar bisa di-iterate seragam
            grouped = [(g, grouped[g]) for g in top_groups]
        else:
            grouped = [(g, group) for g, group in grouped]

        for group_val, subset in grouped:
            fig.add_trace(go.Histogram(
                x=subset[x_col].tolist(),
                nbinsx=30,
                name=str(group_val),
                opacity=0.6
            ))
        fig.update_layout(barmode='overlay')
    else:
        fig.add_trace(go.Histogram(x=dc[x_col].tolist(), nbinsx=30))

    fig.update_layout(title=f'Histogram: {x_col}', xaxis_title=x_col, yaxis_title='Count')
    return fig, None


def build_box_chart(dc, x_col, y_col, color_col):
    if y_col:
        dc[y_col] = pd.to_numeric(dc[y_col], errors='coerce')
        dc = dc.dropna(subset=[y_col])
        if len(dc) == 0:
            return None, "Kolom Y harus berisi angka murni."
        dc[x_col] = dc[x_col].astype(str)
        fig = px.box(dc, x=x_col, y=y_col, color=color_col, title=f'{y_col} per {x_col}')
    else:
        dc[x_col] = pd.to_numeric(dc[x_col], errors='coerce')
        dc = dc.dropna(subset=[x_col])
        if len(dc) == 0:
            return None, "Kolom X harus berisi angka murni."
        fig = px.box(dc, y=x_col, color=color_col, title=f'Distribusi {x_col}')
    return fig, None


def build_violin_chart(dc, x_col, y_col, color_col):
    if y_col:
        dc[y_col] = pd.to_numeric(dc[y_col], errors='coerce')
        dc = dc.dropna(subset=[y_col])
        if len(dc) == 0:
            return None, "Kolom Y harus berisi angka murni."
        dc[x_col] = dc[x_col].astype(str)
        fig = px.violin(dc, x=x_col, y=y_col, color=color_col, box=True,
                        points='outliers', title=f'{y_col} per {x_col}')
    else:
        dc[x_col] = pd.to_numeric(dc[x_col], errors='coerce')
        dc = dc.dropna(subset=[x_col])
        if len(dc) == 0:
            return None, "Kolom X harus berisi angka murni."
        fig = px.violin(dc, y=x_col, color=color_col, box=True,
                        points='outliers', title=f'Distribusi {x_col}')
    return fig, None


def build_scatter_chart(dc, x_col, y_col, color_col=None):
    dc = prepare_numeric_df(dc, [x_col, y_col])
    if dc.empty:
        return None, "Data X atau Y tidak valid."

    if len(dc) > 3000:
        dc = dc.sample(3000, random_state=42)

    fig = go.Figure()

    if color_col and color_col in dc.columns:
        # Kelompokkan per nilai unik color_col, lalu tambahkan satu trace per grup
        for group_val in sorted(dc[color_col].dropna().unique()):
            subset = dc[dc[color_col] == group_val]
            fig.add_trace(go.Scatter(
                x=subset[x_col].tolist(),
                y=subset[y_col].tolist(),
                mode='markers',
                name=str(group_val),
                marker=dict(opacity=0.7, size=8, line=dict(width=0.5, color='#161b22'))
            ))
    else:
        fig.add_trace(go.Scatter(
            x=dc[x_col].tolist(),
            y=dc[y_col].tolist(),
            mode='markers',
            marker=dict(opacity=0.7, size=8, line=dict(width=0.5, color='#161b22'))
        ))

    fig.update_layout(
        title=f'Scatter Plot: {x_col} vs {y_col}',
        xaxis_title=x_col,
        yaxis_title=y_col
    )

    return fig, None


def build_line_chart(dc, x_col, y_col, color_col):
    dc = prepare_numeric_df(dc, [y_col])
    dc = dc.dropna(subset=[x_col, y_col])

    if dc.empty:
        return None, "Kolom Y harus numerik."

    # Sorting berdasarkan tipe data X
    if pd.api.types.is_datetime64_any_dtype(dc[x_col]):
        dc = dc.sort_values(x_col)
    elif pd.api.types.is_numeric_dtype(dc[x_col]):
        dc = dc.sort_values(x_col)
    else:
        # String atau kategori: biarkan urutan abjad (atau sesuai urutan data)
        dc[x_col] = dc[x_col].astype(str)
        dc = dc.sort_values(x_col)

    if len(dc) > 3000:
        dc = dc.iloc[::max(1, len(dc) // 3000)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dc[x_col] if not pd.api.types.is_numeric_dtype(dc[x_col]) else dc[x_col].tolist(),
        y=dc[y_col].tolist(),
        mode='lines'
    ))
    fig.update_layout(
        title=f'Tren: {x_col} vs {y_col}',
        xaxis_title=x_col,
        yaxis_title=y_col
    )
    return fig, None


def build_pie_chart(dc, x_col, y_col, color_col):
    counts = dc[x_col].value_counts().head(15).reset_index()
    counts.columns = [x_col, 'Jumlah']
    counts[x_col] = counts[x_col].astype(str)
    fig = px.pie(counts, names=x_col, values='Jumlah', title=f'Pie Chart: {x_col} (Top 15)')
    return fig, None


def build_time_series(dc, x_col, y_col, color_col):
    dc[y_col] = pd.to_numeric(dc[y_col], errors='coerce')
    dc[x_col] = pd.to_datetime(dc[x_col], errors='coerce')
    dc = dc.dropna(subset=[x_col, y_col]).sort_values(x_col)
    if len(dc) == 0:
        return None, "Kolom X gagal dibaca sebagai waktu (Datetime)."
    if len(dc) > 3000:
        dc = dc.iloc[::max(1, len(dc) // 3000)]
    fig = px.line(dc, x=x_col, y=y_col, color=color_col, title=f'Tren Waktu: {y_col}')
    fig.update_xaxes(rangeslider_visible=True)
    return fig, None


def build_heatmap(dc, numeric_cols):
    if len(numeric_cols) < 2:
        return None, "Butuh minimal 2 kolom numerik untuk Heatmap."

    # Hitung matriks korelasi
    corr = dc[numeric_cols].corr().fillna(0)

    # Buat heatmap manual dengan go.Heatmap (pakai list, bukan numpy)
    fig = go.Figure(go.Heatmap(
        z=corr.values.tolist(),
        x=corr.columns.tolist(),
        y=corr.columns.tolist(),
        colorscale='RdBu',
        zmid=0,
        text=corr.round(2).astype(str).values.tolist(),
        texttemplate='%{text}'
    ))

    fig.update_layout(title='Correlation Heatmap')

    return fig, None