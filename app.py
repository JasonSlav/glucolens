from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import base64
import time
import glob

# Import modul internal
from utils.data_processing import detect_column_types, generate_insights
from utils.themes import apply_dark
from charts.builders import (
    build_bar_chart, build_histogram, build_box_chart, build_violin_chart,
    build_scatter_chart, build_line_chart, build_pie_chart, build_time_series, build_heatmap
)

app = Flask(__name__)
app.secret_key = 'capstone-edv-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

UPLOAD_FOLDER = 'temp_data'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Session helpers ─────────────────────────────────────────────────────────
def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = base64.b64encode(os.urandom(16)).decode('utf-8')
    return session['session_id']

def cleanup_old_files():
    now = time.time()
    for f in glob.glob(os.path.join(UPLOAD_FOLDER, "*.parquet")):
        if os.stat(f).st_mtime < now - 3600:
            try:
                os.remove(f)
            except OSError:
                pass

def store_dataset(sid, df):
    cleanup_old_files()
    filepath = os.path.join(UPLOAD_FOLDER, f"{sid}.parquet")
    df.to_parquet(filepath, index=False)

def get_dataset(sid):
    path = os.path.join(UPLOAD_FOLDER, f"{sid}.parquet")
    return pd.read_parquet(path) if os.path.exists(path) else None

# ── Chart generation coordinator ────────────────────────────────────────────
CHART_BUILDERS = {
    'bar': build_bar_chart,
    'histogram': build_histogram,
    'box': build_box_chart,
    'violin': build_violin_chart,
    'scatter': build_scatter_chart,
    'line': build_line_chart,
    'pie': build_pie_chart,
    'time_series': build_time_series,
    'heatmap': build_heatmap
}

def generate_chart(df, chart_type, x_col, y_col=None, color_col=None):
    try:
        dc = df.copy()

        if chart_type != 'heatmap':
            cols_to_check = [c for c in [x_col, y_col] if c]
            if cols_to_check:
                dc = dc.dropna(subset=cols_to_check)
            if len(dc) == 0:
                return None, "Data kosong setelah drop NaN. Pilih kolom lain."

        if color_col and chart_type != 'heatmap':
            dc[color_col] = dc[color_col].astype(str)

        builder = CHART_BUILDERS.get(chart_type)
        if not builder:
            return None, "Jenis visualisasi tidak didukung."

        if chart_type == 'heatmap':
            # Dapatkan daftar numerik dari session yang sudah tersimpan
            ct = detect_column_types(dc)
            numeric_cols = ct['numeric']
            fig, error_msg = build_heatmap(dc, numeric_cols)
        else:
            fig, error_msg = builder(dc, x_col, y_col, color_col)

        if error_msg:
            return None, error_msg

        apply_dark(fig, is_heatmap=(chart_type == 'heatmap'))
        return json.loads(fig.to_json()), None

    except Exception as e:
        import traceback; traceback.print_exc()
        return None, f"Error dari sistem Plotly: {str(e)}"

# ── Menyimpan col_types di session agar tidak perlu detect ulang ───────────
def get_column_types():
    """Ambil col_types dari session, jika tidak ada kembalikan None."""
    return session.get('col_types')

def set_column_types(ct):
    session['col_types'] = ct

# ── Routes ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file'}), 400
    f = request.files['file']
    if not f.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Hanya CSV yang didukung'}), 400
    try:
        df = None
        for enc in ('utf-8', 'latin-1', 'cp1252'):
            try:
                df = pd.read_csv(f, encoding=enc)
                f.seek(0)
                break
            except UnicodeDecodeError:
                f.seek(0)
        if df is None or df.empty:
            return jsonify({'error': 'Dataset kosong atau tidak bisa dibaca'}), 400

        sid = get_session_id()
        store_dataset(sid, df)

        ct = detect_column_types(df)
        set_column_types(ct)   # simpan di session

        insights = generate_insights(df, ct)

        return jsonify({
            'success': True,
            'filename': f.filename,
            'shape': {'rows': len(df), 'cols': len(df.columns)},
            'col_types': ct,
            'insights': insights,
            'has_datetime': len(ct['datetime']) > 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate_chart', methods=['POST'])
def gen_chart():
    body = request.json or {}
    df = get_dataset(get_session_id())
    if df is None:
        return jsonify({'error': 'Dataset belum diupload atau sesi kadaluarsa'}), 400

    chart_type = body.get('chart_type', 'bar')
    x_col = body.get('x_col') or None
    y_col = body.get('y_col') or None
    color_col = body.get('color_col') or None

    if chart_type != 'heatmap' and not x_col:
        return jsonify({'error': 'Pilih kolom X terlebih dahulu'}), 400

    for lbl, col in (('X', x_col), ('Y', y_col), ('Color', color_col)):
        if col and col not in df.columns:
            return jsonify({'error': f"Kolom {lbl} '{col}' tidak ada di dataset"}), 400

    result, err = generate_chart(df, chart_type, x_col, y_col, color_col)
    if err:
        return jsonify({'error': err}), 400
    return jsonify({'success': True, 'plotly_json': result})

@app.route('/debug_col', methods=['POST'])
def debug_col():
    df = get_dataset(get_session_id())
    if df is None:
        return jsonify({'error': 'Dataset belum diupload'}), 400
    col = (request.json or {}).get('col')
    if not col or col not in df.columns:
        return jsonify({'error': 'Kolom tidak ditemukan'}), 400
    return jsonify({
        'col': col, 'dtype': str(df[col].dtype),
        'sample': [str(v) for v in df[col].dropna().head(5).tolist()],
        'nunique': int(df[col].nunique()),
        'null_count': int(df[col].isnull().sum()),
    })

if __name__ == '__main__':
    app.run(debug=True)