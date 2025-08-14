import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
from cleaning_pipeline import clean_data
from eda_generator import generate_eda_report
from utils import allowed_file
import logging
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024

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
            
            cleaned_filepath, log_report = clean_data(filepath, app.config['OUTPUT_FOLDER'])
            logging.info("Data cleaning pipeline completed.")
            
            eda_report_path = generate_eda_report(cleaned_filepath, app.config['OUTPUT_FOLDER'])
            logging.info("EDA report generated.")
            
            return jsonify({
                'message': 'File processed successfully',
                'cleaned_file': os.path.basename(cleaned_filepath),
                'eda_report': os.path.basename(eda_report_path)
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
        return send_from_directory(app.config['OUTPUT_FOLDER'], filename)
    except FileNotFoundError:
        logging.error(f"EDA report not found: {filename}")
        return jsonify({'error': 'Report not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
