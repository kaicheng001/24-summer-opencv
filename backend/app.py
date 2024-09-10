from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import cv2
from werkzeug.utils import secure_filename  # 确保文件名安全
from utils.image_processing import apply_area_mask, segment_image, replace_background

app = Flask(__name__)

# 获取当前文件所在的目录（即backend目录）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置上传和处理后的文件夹路径
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
PROCESSED_FOLDER = os.path.join(BASE_DIR, 'processed')

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
    
    # 安全地保存文件名
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({'filepath': filepath}), 200

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files.get('file')
    action = request.form.get('action')

    if not file or not action:
        return jsonify({'error': 'Filepath or action not provided'}), 400

    # 安全地保存文件名
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    print('File uploaded successfully')

    # 读取图像
    image = cv2.imread(file_path)
    if image is None:
        return jsonify({'error': 'File not found or could not be read'}), 400

    # 根据不同的操作调用不同的函数
    if action == 'area_mask':
        x = int(request.form.get('x', 50))
        y = int(request.form.get('y', 50))
        w = int(request.form.get('w', 100))
        h = int(request.form.get('h', 100))
        processed_image = apply_area_mask(image, x, y, w, h)
    elif action == 'segmentation':
        processed_image = segment_image(image)
    elif action == 'background_change':
        background_filename = request.form.get('background_path', 'bg.jpg')
        background_path = os.path.join(BASE_DIR, 'static', 'backgrounds', background_filename)
    
        # Debugging: Check if background_path is valid
        print(f"Background path: {background_path}")
    
        processed_image = replace_background(image, background_path)

    else:
        return jsonify({'error': 'Invalid action'}), 400

    # 保存处理后的图像，使用 'processed_' 作为前缀
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_' + filename)

    # Debug 打印，确认路径
    print(f"Saving processed image to: {processed_image_path}")

    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, processed_image)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200

# 用于提供上传的图片的静态文件路径
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 用于提供处理后的图片的静态文件路径
@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
