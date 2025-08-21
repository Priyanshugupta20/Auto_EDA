import os
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from flask_cors import CORS
from pathlib import Path

from .utils.config import (
    UPLOAD_FOLDER,
    OUTPUT_FOLDER,
    FRONTEND_DIR,
    MAX_CONTENT_LENGTH
)
from .utils.helper import setup_logging, allowed_file
from .data_loader import load_data
from .data_types import fix_data_types, identify_columns
from .data_cleaning import normalize_text_columns, remove_duplicates, handle_missing_values, handle_outliers
from .feature_scaling import scale_numerical_columns
from .reporting import save_cleaned_data
from .eda.eda import generate_report, data_overview

# Setup logging and app
setup_logging()
app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / 'templates'),
    static_folder=str(FRONTEND_DIR / 'static')
)
CORS(app)

# Config
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # e.g., 100MB

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(RequestEntityTooLarge)
def handle_large_file(error):
    return jsonify({'error': 'File too large. Max limit is 100MB.'}), 413


@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    try:
        file_id = request.form['file_id']
        chunk_index = request.form['chunk_index']
        file = request.files['file']

        chunk_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        os.makedirs(chunk_dir, exist_ok=True)

        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index}")
        file.save(chunk_path)

        return jsonify({'message': f'Chunk {chunk_index} uploaded successfully'}), 200

    except Exception as e:
        logging.exception(f"Error during chunk upload: {e}")
        return jsonify({'error': 'Chunk upload failed'}), 500


@app.route('/merge_chunks', methods=['POST'])
def merge_chunks():
    try:
        data = request.get_json()
        file_id = data['file_id']
        original_filename = secure_filename(data['filename'])

        chunk_dir = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
        merged_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)

        # Merge chunks
        chunk_files = sorted(os.listdir(chunk_dir), key=lambda x: int(x.split('_')[1]))
        with open(merged_path, 'wb') as outfile:
            for chunk_file in chunk_files:
                with open(os.path.join(chunk_dir, chunk_file), 'rb') as infile:
                    outfile.write(infile.read())

        # Clean up chunks
        for chunk_file in chunk_files:
            os.remove(os.path.join(chunk_dir, chunk_file))
        os.rmdir(chunk_dir)

        # Run EDA + Cleaning pipeline
        log_list = []
        df_before = load_data(merged_path)

        overview = data_overview(df_before)
        df = df_before.copy()

        df, log = fix_data_types(df)
        log_list.append(log)

        columns_dtype = identify_columns(df)
        df = normalize_text_columns(df, columns_dtype['others'])

        df, log = remove_duplicates(df)
        log_list.append(log)

        df, log = handle_missing_values(df, columns_dtype['numerical'], columns_dtype['categorical'], columns_dtype['datetime'])
        log_list.append(log)

        df, log = handle_outliers(df)
        log_list.append(log)

        cleaned_filename = save_cleaned_data(df)
        report_filename = generate_report(df)

        logging.info("File processed and EDA report generated.")

        return jsonify({
            'message': 'File processed successfully',
            'overview': overview,
            'log_report': log_list,
            'cleaned_file': cleaned_filename,
            'eda_report': report_filename
        }), 200

    except Exception as e:
        logging.exception(f"Error during file merge and processing: {e}")
        return jsonify({'error': 'Failed to merge and process file'}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404


@app.route('/eda/<filename>', methods=['GET'])
def serve_eda_report(filename):
    try:
        safe_filename = secure_filename(filename)
        file_path = Path(app.config['OUTPUT_FOLDER']) / safe_filename

        if not file_path.exists():
            logging.error(f"EDA report not found: {safe_filename}")
            return jsonify({'error': 'Report not found'}), 404

        return send_file(file_path, mimetype='text/html')

    except Exception as e:
        logging.exception(f"Error serving EDA report: {e}")
        return jsonify({'error': 'Internal server error'}), 500
