from flask import Flask, render_template, request, send_from_directory, jsonify, send_file
import os
import cv2
import base64
import io
from io import BytesIO
import numpy as np
from werkzeug.utils import secure_filename  # 确保文件名安全
from utils.image_processing import (apply_area_mask, segment_image, replace_background,concave,convex,apply_mosaic_effect,draw_on_mask,
                                    extract_foreground, apply_rgb_filter, overlay_images,create_text_image, rotate_image_with_transparency, draw_red_dot)
from utils.filter import (apply_hot_filter,apply_cool_filter,apply_rainbow_filter,apply_pink_filter, apply_spring_filter, 
                          apply_summer_filter, apply_winter_filter, apply_ocean_filter, apply_autumn_filter, apply_bone_filter, 
                          apply_jet_filter, apply_hsv_filter, cartoonize_image, sketch_image)
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

mask = None

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
    print(998)
    file = request.files.get('file')
    action = request.form.get('action')
    version = request.form.get('version')
    if not file or not action:
        return jsonify({'error': 'Filepath or action not provided'}), 400

    # 安全地保存文件名
    filename = secure_filename(file.filename)

    # 加入版本号防止覆盖##########
    base_filename, ext = os.path.splitext(filename)
    processed_filename = f"{base_filename}_v{version}{ext}"

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
        



    #以下是14中滤镜效果    
    elif action == 'Hot':
        processed_image = apply_hot_filter(image)
    elif action == 'Cool':
        processed_image = apply_cool_filter(image)
    elif action == 'Rainbow':
        processed_image = apply_rainbow_filter(image)
    elif action == 'Pink':
        processed_image = apply_pink_filter(image)
    elif action == 'Spring':
        processed_image = apply_spring_filter(image)
    elif action == 'Summer':
        processed_image = apply_summer_filter(image)
    elif action == 'Winter':
        processed_image = apply_winter_filter(image)
    elif action == 'Ocean':
        processed_image = apply_ocean_filter(image)
    elif action == 'Autumn':
        processed_image = apply_autumn_filter(image)
    elif action == 'Bone':
        processed_image = apply_bone_filter(image)
    elif action == 'Jet':
        processed_image = apply_jet_filter(image)
    elif action == 'HSV':
        processed_image = apply_hsv_filter(image)
    elif action == 'Cartoon':
        processed_image = cartoonize_image(image)
    elif action == 'Sketch':
        processed_image = sketch_image(image)

    else:
        return jsonify({'error': 'Invalid action'}), 400

    # 保存处理后的图像，使用 'processed_' 作为前缀
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'],f'processed_{processed_filename}' )

    # Debug 打印，确认路径
    print(f"Saving processed image to: {processed_image_path}")

    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, processed_image)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200

@app.route('/processcanvas', methods=['POST'])
def process_image_canvas():
    print("process image app.py")
    file = request.files.get('file')
    action = request.form.get('action')
    version = request.form.get('version')
    if not file or not action:
        return jsonify({'error': 'File or action not provided'}), 400

    filename = secure_filename(file.filename)
    # 加入版本号防止覆盖##########
    base_filename, ext = os.path.splitext(filename)
    processed_filename = f"{base_filename}_v{version}{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    image = cv2.imread(file_path)
    if image is None:
        return jsonify({'error': 'File not found or could not be read'}), 400

    if action == 'crop':
        print("action====crop")
        x = float(request.form.get('x'))
        y = float(request.form.get('y'))
        print(x,y)
        width = float(request.form.get('width'))
        height = float(request.form.get('height'))
        rotation = float(request.form.get('rotation'))
        #换成整数
        # 如果确实需要整数，你可以在适当的时候再进行转换
        x = int(x)  # 根据需求将 x 转换为整数
        y = int(y)
        width = int(width)
        height = int(height)
        rotation=int(rotation)
        # 中心旋转裁剪
        center = (x + width // 2, y + height // 2)
        matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
        rotated = cv2.warpAffine(image, matrix, (image.shape[1], image.shape[0]))
        processed_image = rotated[y:y + height, x:x + width]
    elif action == 'rotate':
        angle = float(request.form.get('angle'))
        resizeheight = float(request.form.get('height'))
        resizeweight = float(request.form.get('width'))
        resizeheight=int(resizeheight)
        resizeweight=int(resizeweight)
        image = cv2.resize(image,(resizeweight,resizeheight),interpolation=cv2.INTER_LINEAR)
        processed_image = rotate_image_with_transparency(image,angle*2)
    else:
        return jsonify({'error': 'Invalid action'}), 400
    # 保存处理后的图像，使用 'processed_' 作为前缀
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'],f'processed_{processed_filename}' )###原来是：'processed_' + filename

    # Debug 打印，确认路径
    print(f"Saving processed image to: {processed_image_path}")

    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, processed_image)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200

@app.route('/processtrans', methods=['POST'])
def process_image_convave():
    print("process image app.py")
    file = request.files.get('file')
    action = request.form.get('action')
    version = request.form.get('version')
    if not file or not action:
        return jsonify({'error': 'File or action not provided'}), 400

    filename = secure_filename(file.filename)
    # 加入版本号防止覆盖##########
    base_filename, ext = os.path.splitext(filename)
    processed_filename = f"{base_filename}_v{version}{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    
    image = cv2.imread(file_path)
    if image is None:
        return jsonify({'error': 'File not found or could not be read'}), 400

    if action == 'aotou':
        print("action====aotou")
        x = float(request.form.get('x'))
        y = float(request.form.get('y'))
        print(x,y)
        #换成整数
        # 如果确实需要整数，你可以在适当的时候再进行转换
        x = int(x)  # 根据需求将 x 转换为整数
        y = int(y)
        # 中心旋转裁剪
        processed_image = concave(image,x,y)
    elif action == 'tutou':
        x = float(request.form.get('x'))
        y = float(request.form.get('y'))
        print(x,y)
        #换成整数
        # 如果确实需要整数，你可以在适当的时候再进行转换
        x = int(x)  # 根据需求将 x 转换为整数
        y = int(y)
        processed_image = convex(image,[x,y])
    else:
        return jsonify({'error': 'Invalid action'}), 400
    # 保存处理后的图像，使用 'processed_' 作为前缀
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'],f'processed_{processed_filename}' )###原来是：'processed_' + filename

    # Debug 打印，确认路径
    print(f"Saving processed image to: {processed_image_path}")

    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, processed_image)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200

@app.route('/processmosaic', methods=['POST'])
def process_mosaic():
    global mask
    # 处理图像文件
    x = float(request.form.get('x'))
    y = float(request.form.get('y'))
    x = int(x)  # 根据需求将 x 转换为整数
    y = int(y)
    size = int(request.form.get('size'))
    # 获取 Base64 图像数据
    image_base64 = request.form.get('image_base64', '')
    action = request.form.get('action')
    if not image_base64:
        print(999)
        return jsonify({'error': 'No image data provided'}), 400
        
        # 解码 Base64 图像数据
    else:
        print(98)
    try:
        image_data = base64.b64decode(image_base64)
    except base64.binascii.Error as e:
        return jsonify({'error': 'Invalid Base64 image data'}), 400
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if(action == 'mosaic'):
    # 对图像进行马赛克处理
        processed_img = apply_mosaic_effect(img, x, y, size)
    elif(action == 'mask'):
        processed_img = draw_on_mask(img,mask,size,x,y)
    elif(action == 'huahua'):
        processed_img = draw_red_dot(img, x, y, size)
    # 将处理后的图像再次编码为 Base64
    _, buffer = cv2.imencode('.jpg', processed_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    print("app.pyover")
    # 返回 Base64 编码的图像
    return jsonify({'image_base64': img_base64})


@app.route('/okmosaic', methods=['POST'])
def ok_savemosaic():
    file = request.files.get('file')
    version = request.form.get('version')
    if not file :
        return jsonify({'error': 'File or action not provided'}), 400
    
    filename = secure_filename(file.filename)
    # 加入版本号防止覆盖##########
    base_filename, ext = os.path.splitext(filename)
    processed_filename = f"{base_filename}_v{version}{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    # 获取 Base64 图像数据
    image_base64 = request.form.get('image_base64', '')
    if not image_base64:
        print(999)
        return jsonify({'error': 'No image data provided'}), 400
        
        # 解码 Base64 图像数据
    else:
        print(98)
    try:
        image_data = base64.b64decode(image_base64)
    except base64.binascii.Error as e:
        return jsonify({'error': 'Invalid Base64 image data'}), 400
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'],f'processed_{processed_filename}' )
    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, img)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200




@app.route('/okmask', methods=['POST'])
def maskok():
    global mask
    file = request.files.get('file')
    version = request.form.get('version')
    if not file :
        return jsonify({'error': 'File or action not provided'}), 400
    
    filename = secure_filename(file.filename)
    # 加入版本号防止覆盖##########
    base_filename, ext = os.path.splitext(filename)
    processed_filename = f"{base_filename}_v{version}{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    # 获取 Base64 图像数据
    image_base64_1 = request.form.get('image_base64_1', '')
    if not image_base64_1:
        print(999)
        return jsonify({'error': 'No image data provided'}), 400
        
        # 解码 Base64 图像数据
    else:
        print(98)
    try:
        image_data_1 = base64.b64decode(image_base64_1)
    except base64.binascii.Error as e:
        return jsonify({'error': 'Invalid Base64 image data'}), 400
    img_array_1 = np.frombuffer(image_data_1, np.uint8)
    imgtemp = cv2.imdecode(img_array_1, cv2.IMREAD_COLOR)
    img=extract_foreground(imgtemp,mask)
    mask=None
    processed_image_path = os.path.join(app.config['PROCESSED_FOLDER'],f'processed_{processed_filename}' )
    # 确认处理的图像保存成功
    success = cv2.imwrite(processed_image_path, img)
    if not success:
        return jsonify({'error': 'Failed to save the processed image'}), 500

    # 返回处理后的图像路径（前端可以使用此路径）
    return jsonify({'filepath': f'/processed/{os.path.basename(processed_image_path)}'}), 200


@app.route('/setmask', methods=['POST'])
def maskset():
    global mask
    file = request.files.get('file')
    if not file :
        return jsonify({'error': 'File or action not provided'}), 400
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    image = cv2.imread(file_path)
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    return jsonify({'error': 'masksetover'}), 500


@app.route('/processInsert', methods=['POST'])
def process_insert():
    # 处理图像文件
    x = float(request.form.get('x'))
    y = float(request.form.get('y'))
    x = int(x)  # 根据需求将 x 转换为整数
    y = int(y)
    # 获取 Base64 图像数据
    image_base64 = request.form.get('image_base64', '')
    if not image_base64:
        print(999)
        return jsonify({'error': 'No image data provided'}), 400
        
        # 解码 Base64 图像数据
    else:
        print(98)
    try:
        image_data = base64.b64decode(image_base64)
    except base64.binascii.Error as e:
        return jsonify({'error': 'Invalid Base64 image data'}), 400
    img_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
    ###
    image_base64_1 = request.form.get('image_base64_1', '')
    if not image_base64_1:
        print(999)
        return jsonify({'error': 'No image data provided'}), 400
        
        # 解码 Base64 图像数据
    else:
        print(98)
    try:
        image_data1 = base64.b64decode(image_base64_1)
    except base64.binascii.Error as e:
        return jsonify({'error': 'Invalid Base64 image data'}), 400
    img_array1 = np.frombuffer(image_data1, np.uint8)
    img1 = cv2.imdecode(img_array1, cv2.IMREAD_UNCHANGED)

    # 对图像进行叠加处理
    processed_img = overlay_images(img,img1, x, y)

    # 将处理后的图像再次编码为 Base64
    _, buffer = cv2.imencode('.png', processed_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    print("app.pyover")
    # 返回 Base64 编码的图像
    return jsonify({'image_base64': img_base64})




#证件照制作rgb
@app.route('/apply-rgb-filter', methods=['POST'])
def apply_rgb_filter_endpoint():
    file = request.files['file']
    R = int(request.form.get('R', 0))
    G = int(request.form.get('G', 0))
    B = int(request.form.get('B', 0))

    # 读取上传的图像
    img_array = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # 应用 RGB 滤镜
    result_image = apply_rgb_filter(image, R, G, B)

    # 将处理后的图像编码为 JPEG 格式返回给前端
    _, img_encoded = cv2.imencode('.png', result_image)
    return send_file(io.BytesIO(img_encoded), mimetype='image/jpeg')



# 用于应用滤镜
@app.route('/processfilter', methods=['POST'])
def apply_filters():
    data = request.json
    filter_type = data.get('filterType')
    image_data = data.get('image')  # Expecting base64 encoded image

    # Define a mapping from filter types to filter functions
    filter_mapping = {
        'Pink': apply_pink_filter,
        'Spring': apply_spring_filter,
        'Summer': apply_summer_filter,
        'Winter': apply_winter_filter,
        'Ocean': apply_ocean_filter,
        'Autumn': apply_autumn_filter,
        'Bone': apply_bone_filter,
        'Jet': apply_jet_filter,
        'HSV': apply_hsv_filter,
        'Cartoon': cartoonize_image,
        'Sketch': sketch_image
    }

    # Get the filter function based on the filter type
    filter_function = filter_mapping.get(filter_type)

    if filter_function:
        output = process_image(image_data, filter_function)
        return send_file(output, mimetype='image/png', as_attachment=True, download_name='filtered_image.png')
    else:
        return jsonify({'error': 'Invalid filter type'}), 400

#用于浏览文件夹中的图片
# @app.route('/browse', methods=['POST'])
# def browse_images():
#     data = request.get_json()
#     files = data.get('files', [])
    
#     images = get_images_from_files.get_images_from_files(files)

#     return jsonify({'images': images})

# 用于提供上传的图片的静态文件路径
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 用于提供处理后的图片的静态文件路径
@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route('/processtext', methods=['POST'])
def textimage():
    input_text = request.form.get('inputtext')
    processed_img = create_text_image(input_text)
    # 将处理后的图像再次编码为 Base64
    _, buffer = cv2.imencode('.png', processed_img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    print("app.pyover")
    # 返回 Base64 编码的图像
    return jsonify({'image_base64': img_base64})


if __name__ == '__main__':
    app.run(debug=True)
