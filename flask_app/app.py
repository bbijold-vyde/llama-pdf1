import os
from flask import Flask, request, send_file, jsonify, render_template
from threading import Thread
import process
import pandas as pd

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
CONVERTED_FOLDER =  'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

processing_status = {
    "total_files": 0,
    "processed_files": 0,
    "current_file": ""
}


def process_files_thread():
    global processing_status
    # for each uploades - call pdf convert
    files = os.listdir(UPLOAD_FOLDER)
    # for filename in pdffiles:
    #     process.pdf_convert(filename)
    #     print("pages converted to png")
    # files = os.listdir(CONVERTED_FOLDER)
    processing_status["total_files"] = len(files)
    processing_status["processed_files"] = 0

    
    
    for filename in files:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            processing_status["current_file"] = filename
            process.process_document(file_path)
            processing_status["processed_files"] += 1
    
    processing_status["current_file"] = "Processing complete"

@app.route('/download_xlsx', methods=['GET'])
def download_xlsx():
    output_csv_path = 'outputs/output.csv'
    output_xlsx_path = 'outputs/output.xlsx'
    df = pd.read_csv(output_csv_path)
    df.to_excel(output_xlsx_path, index=False)
    return send_file(output_xlsx_path, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return "No file part", 400
    files = request.files.getlist('files[]')
    for file in files:
        if file.filename == '':
            return "No selected file", 400
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
    return "Files uploaded successfully", 200

@app.route('/delete', methods=['POST'])
def delete_file(): #duplicate delete for pngs
    filename = request.form['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return "File deleted successfully", 200
    else:
        return "File not found", 404

@app.route('/delete_all', methods=['POST'])
def delete_all_files(): #duplicate delete for pngs
    files = os.listdir(UPLOAD_FOLDER)
    for file in files:
        file_path = os.path.join(UPLOAD_FOLDER, file)
        os.remove(file_path)
    return "All files deleted successfully", 200

@app.route('/process', methods=['POST'])
def process_files():
    thread = Thread(target=process_files_thread)
    thread.start()
    return "Processing started", 200

@app.route('/status', methods=['GET'])
def status():
    return jsonify(processing_status)

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/download_csv', methods=['GET'])
def download_csv():
    return send_file('output.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5002)

