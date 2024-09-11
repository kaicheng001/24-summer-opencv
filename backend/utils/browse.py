import os
from PIL import Image
import base64
from io import BytesIO

# 支持的图片格式
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']

def get_images_from_files(files):
    images = []
    for file in files:
        file_ext = os.path.splitext(file)[1].lower()
        if file_ext in IMAGE_EXTENSIONS:
            try:
                with Image.open(file) as img:
                    img_io = BytesIO()
                    img.save(img_io, 'PNG')
                    img_io.seek(0)
                    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
                    images.append(f"data:image/png;base64,{img_base64}")
            except Exception as e:
                print(f"无法打开图片 {file}: {e}")
    return images
