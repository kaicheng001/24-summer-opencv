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

def draw_on_mask(image, mask, thickness, x, y):
    """
    在输入图像上指定坐标位置涂抹半透明绿色，并更新掩码。
    
    参数：
    - image: 输入图像，形状为 (H, W, 3) 的 numpy 数组
    - mask: 输入掩码，形状为 (H, W) 的全局变量
    - thickness: 画笔粗细
    - x, y: 涂抹位置的坐标
    
    返回：
    - result_image: 涂抹后的图像
    """
    # 复制图像，防止修改原图像
    result_image = image.copy()
    
    # 创建一个与图像相同形状的半透明绿色图层
    overlay = result_image.copy()
    cv2.circle(overlay, (x, y), thickness, (0, 255, 0), -1)  # 绿色 BGR 颜色

    # 叠加图层并设置透明度
    alpha = 0.5  # 半透明度
    cv2.addWeighted(overlay, alpha, result_image, 1 - alpha, 0, result_image)

    # 更新掩码，将涂抹区域的值设置为 1
    cv2.circle(mask, (x, y), thickness, 1, -1)
    
    return result_image


def extract_foreground(image, mask):
    """
    根据掩码提取图像中的前景区域。
    
    参数：
    - image: 输入的彩色图像，形状为 (H, W, 3) 的 numpy 数组。
    - mask: 输入的掩码图像，形状为 (H, W) 的二值化掩码（值为0或1），numpy 数组。
    
    返回：
    - foreground: 通过掩码提取的前景图像。
    """
    # 确保掩码是二值掩码（0 和 1）
    mask = np.where(mask > 0, 1, 0).astype(np.uint8)
    
    # 使用掩码提取前景
    foreground = cv2.bitwise_and(image, image, mask=mask)
    
    return foreground


def apply_rgb_filter(image, R, G, B):
    """
    输入图像和背景的 RGB 颜色值，返回制作好的证件照（背景颜色已更改）
    
    参数:
    - image: 输入的图像，形状为 (H, W, 3) 的 BGR 图像。
    - R: 背景的红色分量 (0-255)
    - G: 背景的绿色分量 (0-255)
    - B: 背景的蓝色分量 (0-255)
    
    返回:
    - result_image: 制作好的带有指定背景颜色的证件照。
    """
    # 初始化掩码和模型
    mask = np.zeros(image.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)

    # 自动设置一个矩形作为 GrabCut 的初始区域
    height, width = image.shape[:2]
    rect = (10, 10, width - 20, height - 20)  # 假设除边缘部分外，主体在中心

    # 使用 GrabCut 进行图像分割
    cv2.grabCut(image, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

    # 将背景和可能的背景设置为 0，前景和可能的前景设置为 1
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # 获取前景部分
    foreground = image * mask2[:, :, np.newaxis]

    # 创建新的背景颜色
    background = np.full_like(image, [B, G, R], dtype=np.uint8)

    # 使用掩码将背景部分替换为指定颜色
    background = background * (1 - mask2[:, :, np.newaxis])

    # 合并前景和背景
    result_image = cv2.add(foreground, background)

    return result_image