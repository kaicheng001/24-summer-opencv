import cv2
import numpy as np
import os
import random
def process_image(image_path, output_folder, action, additional_params=None):
    image = cv2.imread(image_path)
    
    if action == 'area_mask':
        processed_image = apply_area_mask(image)
    elif action == 'segmentation':
        processed_image = segment_image(image)
    elif action == 'id_photo':
        processed_image = make_id_photo(image, additional_params)
    elif action == 'background_change':
        new_background_path = additional_params.get('background_path')
        processed_image = replace_background(image, new_background_path)
    else:
        raise ValueError(f"Unknown action: {action}")
    
    output_path = os.path.join(output_folder, f'processed_{os.path.basename(image_path)}')
    cv2.imwrite(output_path, processed_image)
    return output_path

def apply_area_mask(image, x=50, y=50, w=100, h=100):
    """
    Applies a Gaussian blur to a specified area of the image.
    """
    sub_img = image[y:y+h, x:x+w]
    sub_img = cv2.GaussianBlur(sub_img, (23, 23), 30)
    image[y:y+h, x:x+w] = sub_img
    return image

def segment_image(image):
    """
    Simple threshold-based image segmentation.
    Converts image to grayscale, applies binary thresholding.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

def make_id_photo(image, params):
    """
    Creates an ID photo by resizing and adjusting the background color.
    Params should include the desired output dimensions and background color.
    """
    desired_width = params.get('width', 300)
    desired_height = params.get('height', 400)
    background_color = params.get('background_color', (255, 255, 255))  # Default to white background

    # Resize image to desired dimensions
    resized_image = cv2.resize(image, (desired_width, desired_height))
    
    # Create a background with the desired color
    background = np.full((desired_height, desired_width, 3), background_color, dtype=np.uint8)
    
    # Combine the image with the background
    combined_image = cv2.addWeighted(resized_image, 1, background, 0, 0)
    
    return combined_image

def replace_background(image, background_path):
    """
    Replaces the background of an image with a new background.
    The image should have a clear foreground (e.g., after segmentation).
    """
    # Debug: Check if the background image path exists
    if not os.path.exists(background_path):
        raise FileNotFoundError(f"Background image not found at {background_path}")
    
    # Load the background image
    background = cv2.imread(background_path)
    if background is None:
        raise FileNotFoundError(f"Could not load background image from {background_path}")
    
    # Resize the background image to match the input image size
    background = cv2.resize(background, (image.shape[1], image.shape[0]))
    
    # Convert the input image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Debug: Check grayscale image properties
    print(f"Grayscale image shape: {gray.shape}, unique values: {np.unique(gray)}")
    
    # Threshold to create a mask (adjust the threshold value if needed)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Debug: Check the mask properties
    print(f"Mask shape: {mask.shape}, unique values: {np.unique(mask)}")
    
    # Create an inverted mask
    mask_inv = cv2.bitwise_not(mask)
    
    # Extract the foreground and background
    fg = cv2.bitwise_and(image, image, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    
    # Debug: Check if foreground and background were created correctly
    print(f"Foreground shape: {fg.shape}, Background shape: {bg.shape}")
    
    # Combine the foreground and the new background
    combined_image = cv2.add(fg, bg)
    
    return combined_image

def concave(src_img, x, y):
    center = (x, y)
    h, w = src_img.shape[:2]
    output = np.zeros_like(src_img)
    radius = min(w, h) // 3  # 自动计算半径为图像尺寸的三分之一

    # 遍历图像的每个像素
    for y in range(h):
        for x in range(w):
            dx = x - center[0]
            dy = y - center[1]
            dist = np.sqrt(dx**2 + dy**2)
            if dist < 1e-5:  # 避免除以零
                continue
            angle = np.arctan2(dy, dx)

            # 计算凹透镜效果下的映射位置
            new_dist = radius * (dist / radius) / (1 + (dist / (2 * radius)))
            new_x = int(center[0] + new_dist * np.cos(angle))
            new_y = int(center[1] + new_dist * np.sin(angle))

            # 边界检查
            if 0 <= new_x < w and 0 <= new_y < h:
                output[y, x] = src_img[new_y, new_x]

    return output
def convex(src_img, center):
    row, col, channel = src_img.shape
    radius = min(col, row) // 3 
    output = np.zeros([row, col, channel], dtype=np.uint8)

    for y in range(row):
        for x in range(col):
            d = ((x - center[0]) ** 2 + (y - center[1]) ** 2) ** 0.5
            if d <= radius:
                nx = int((x - center[0]) * d / radius + center[0])
                ny = int((y - center[1]) * d / radius + center[1])
                output[y, x, :] = src_img[ny, nx, :]
            else:
                output[y, x, :] = src_img[y, x, :]
    return output
def apply_mosaic_effect(img, x, y, mosaic_size=10):
     # 复制输入图像
    img_out = img.copy()

    # 获取图像的行列和通道数
    row, col, channel = img.shape

    # 设置半方块大小
    half_patch = mosaic_size // 2

    # 限制马赛克效果的区域范围
    x_start = max(half_patch, x - half_patch)
    x_end = min(col - half_patch, x + half_patch)
    y_start = max(half_patch, y - half_patch)
    y_end = min(row - half_patch, y + half_patch)

    # 遍历指定的区域并进行马赛克处理
    for i in range(y_start, y_end, mosaic_size):
        for j in range(x_start, x_end, mosaic_size):
            # 随机偏移
            k1 = random.random() - 0.5
            k2 = random.random() - 0.5
            m = np.floor(k1 * (half_patch * 2 + 1))
            n = np.floor(k2 * (half_patch * 2 + 1))

            # 计算随机像素的位置
            h = int((i + m) % row)
            w = int((j + n) % col)

            # 用随机像素的颜色填充当前方块区域
            img_out[i - half_patch:i + half_patch, j - half_patch:j + half_patch, :] = img[h, w, :]

    return img_out