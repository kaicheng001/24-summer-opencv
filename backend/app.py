from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import cv2
import json
from utils.image_processing import apply_area_mask, segment_image, replace_background

app = Flask(__name__)

# 配置上传和处理后的文件夹
UPLOAD_FOLDER = 'uploads/'
PROCESSED_FOLDER = 'processed/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# 确保文件夹存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({'filepath': filepath}), 200

@app.route('/process', methods=['POST'])
def process_image():
    data = request.json
    filepath = data.get('filepath')
    action = data.get('action')
    additional_params = data.get('additional_params', {})

    if not filepath or not action:
        return jsonify({'error': 'Filepath or action not provided'}), 400

    # 读取图像
    image = cv2.imread(filepath)
    if image is None:
        return jsonify({'error': 'File not found or could not be read'}), 400

    # 根据不同的操作调用不同的函数
    if action == 'area_mask':
        x = additional_params.get('x', 50)
        y = additional_params.get('y', 50)
        w = additional_params.get('w', 100)
        h = additional_params.get('h', 100)
        processed_image = apply_area_mask(image, x, y, w, h)
    elif action == 'segmentation':
        processed_image = segment_image(image)
    elif action == 'background_change':
        background_path = additional_params.get('background_path', 'static/backgrounds/bg.jpg')
        processed_image = replace_background(image, background_path)
    else:
        return jsonify({'error': 'Invalid action'}), 400

    # 保存处理后的图像
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_' + os.path.basename(filepath))
    cv2.imwrite(processed_image_path, processed_image)
    
    return jsonify({'filepath': processed_image_path}), 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
