import os
import logging
from flask import Flask, request, jsonify, send_from_directory, render_template, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pathlib import Path

from utils.config import (
    UPLOAD_FOLDER,
    OUTPUT_FOLDER,
    FRONTEND_DIR,
    MAX_CONTENT_LENGTH
)
from utils.helper import setup_logging, allowed_file
from data_loader import load_data
from data_types import fix_data_types, identify_columns
from data_cleaning import normalize_text_columns, remove_duplicates, handle_missing_values, handle_outliers
from feature_scaling import scale_numerical_columns
from reporting import save_cleaned_data, log_cleaning_report
from eda.eda import generate_report, data_overview

# from eda_generator import generate_eda_report
# from utils import allowed_file


setup_logging()

app = Flask(
    __name__,
    template_folder=str(FRONTEND_DIR / 'templates'),
    static_folder=str(FRONTEND_DIR / 'static')
)

CORS(app)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['OUTPUT_FOLDER'] = str(OUTPUT_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            logging.error('No file part in the request')
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            logging.error('No selected file')
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logging.info(f"File uploaded successfully: {filepath}")
            
            log_list = []
            df_before = load_data(filepath)

            overview = data_overview(df_before)
            df = df_before.copy()
            df, log = fix_data_types(df)
            log_list.append(log)
            columns_type = identify_columns(df)
            df = normalize_text_columns(df)
            df = remove_duplicates(df)
            df, log = handle_missing_values(df, columns_type['numerical'], columns_type['categorical'])
            log_list.append(log)
            df = handle_outliers(df)
            cleaned_filename = save_cleaned_data(df)

            logging.info("Data cleaning pipeline completed.")
            
            report_filename = generate_report(df)
            # eda_report_path = generate_eda_report(cleaned_filepath, app.config['OUTPUT_FOLDER'])
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

# @app.route('/eda/<filename>', methods=['GET'])
# def serve_eda_report(filename):
#     try:
#         return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
#     except FileNotFoundError:
#         logging.error(f"EDA report not found: {filename}")
#         return jsonify({'error': 'Report not found'}), 404




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


if __name__ == '__main__':
    app.run()
