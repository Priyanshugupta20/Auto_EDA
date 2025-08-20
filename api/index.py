import os
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pathlib import Path
import shutil

from backend.utils.config import (
    FRONTEND_DIR,
    MAX_CONTENT_LENGTH
)
from backend.utils.helper import setup_logging, allowed_file
from backend.src.data_loader import load_data
from backend.src.data_types import fix_data_types, identify_columns
from backend.src.data_cleaning import normalize_text_columns, remove_duplicates, handle_missing_values, handle_outliers
from backend.src.reporting import save_cleaned_data
from backend.src.eda.eda import generate_report, data_overview

setup_logging()

app = Flask(
    __name__,
    template_folder=str(Path('./frontend/templates')),
    static_folder=str(Path('./frontend/static'))
)

CORS(app)

TMP_DIR = Path("/tmp")
UPLOAD_FOLDER = TMP_DIR / "uploads"
OUTPUT_FOLDER = TMP_DIR / "outputs"

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():

    if UPLOAD_FOLDER.exists():
        shutil.rmtree(UPLOAD_FOLDER)
    if OUTPUT_FOLDER.exists():
        shutil.rmtree(OUTPUT_FOLDER)
        
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    try:
        if 'file' not in request.files:
            logging.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logging.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            original_filename = secure_filename(file.filename)
            file_ext = os.path.splitext(original_filename)[1]
            custom_name = "raw_dataset" + file_ext
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], custom_name)
            file.save(filepath)
            
            logging.info(f"File uploaded successfully: {filepath}")
            
            log_list = []
            df_before = load_data(filepath)

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

            logging.info("Data cleaning pipeline completed.")
            
            report_filename = generate_report(df)

            logging.info("EDA report generated.")
            
            return jsonify({
                'message': 'File processed successfully',
                'overview': overview,
                'log_report': log_list,
                'cleaned_file': cleaned_filename,
                'eda_report': report_filename
            }), 200
        else:
            logging.error(f"File type not allowed: {file.filename}")
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        logging.exception(f"An error occurred during file upload: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        logging.error(f"File not found for download: {filename}")
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
