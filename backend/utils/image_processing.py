import cv2
import numpy as np
import os
import random
from PIL import ImageFont, ImageDraw, Image


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

import cv2
import numpy as np

def overlay_images(img, img1, x, y):
    # 获取 img 和 img1 的尺寸
    h, w, d = img.shape
    h1, w1, d1 = img1.shape  # d1为img1的通道数

    # 检查通道数，确保img1是RGB或RGBA图像
    if d1 not in [3, 4]:
        raise ValueError("Overlay image format not supported. It should be either RGB or RGBA.")

    # 计算 img1 的左上角坐标
    top_left_x = x - w1 // 2
    top_left_y = y - h1 // 2

    # 确保叠加区域在 img 的范围内
    if top_left_x < 0 or top_left_y < 0 or top_left_x + w1 > w or top_left_y + h1 > h:
        raise ValueError("The overlay image exceeds the boundaries of the background image.")

    # 如果 img 是 RGB，转换为 RGBA
    if d == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # 创建一个用于存放结果的图像
    result = img.copy()

    # 叠加图片
    for i in range(h1):
        for j in range(w1):
            if d1 == 4:  # 如果img1是RGBA图像，考虑透明度
                if img1[i, j][3] > 0:  # 透明度大于零
                    alpha = img1[i, j][3] / 255.0  # 归一化到 0-1 之间
                    result[top_left_y + i, top_left_x + j, :3] = (1 - alpha) * result[top_left_y + i, top_left_x + j, :3] + alpha * img1[i, j][:3]
                    result[top_left_y + i, top_left_x + j, 3] = 255  # 设置 alpha 通道为不透明
            else:  # 如果img1是RGB图像，直接复制颜色信息，并设置 alpha 通道为不透明
                result[top_left_y + i, top_left_x + j, :3] = img1[i, j]
                result[top_left_y + i, top_left_x + j, 3] = 255

    return result


def create_text_image(text, font_scale=5, font_color=(255, 255, 255, 255), font_thickness=2, bg_color=(0, 0, 0, 0), image_size=(100, 100)):
    """
    创建一个带有文字的透明背景图片，并返回RGBA格式的图片。

    参数:
    - text: 文字内容 (str)
    - font_scale: 文字大小 (float)
    - font_color: 文字颜色，(R, G, B, A) 格式 (tuple)
    - font_thickness: 文字厚度 (int)
    - bg_color: 背景颜色 (R, G, B, A)，默认为透明背景 (tuple)
    - image_size: 图片大小，默认为(500, 500) (tuple)

    返回:
    - image: 生成的带有文字的RGBA背景图片 (np.array)
    """
    # 设置图片大小
    img_width, img_height = image_size
    
    # 创建一个带透明度的 RGBA 背景图像
    image = np.zeros((img_height, img_width, 4), dtype=np.uint8)
    
    # 设置背景颜色
    image[:, :] = bg_color

    # 使用 OpenCV 内置字体
    font = cv2.FONT_HERSHEY_SIMPLEX

    # 动态计算字体大小
    font_scale = font_scale * min(img_width, img_height) / 500  # 根据图片大小调整字体比例
    
    # 获取文字的尺寸
    text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
    text_width, text_height = text_size

    # 计算文字的居中位置
    text_x = (img_width - text_width) // 2
    text_y = (img_height + text_height) // 2  # 注意：OpenCV的文本是以基线为基准的

    # 绘制文字到图像上（在RGBA图像上绘制文字）
    cv2.putText(image, text, (text_x, text_y), font, font_scale, font_color, font_thickness, cv2.LINE_AA)

    # 返回带有透明背景的 RGBA 图片
    return image


def rotate_image_with_transparency(img, angle):
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    
    (h, w) = img.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # 获取旋转矩阵，并附加旋转角度
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
    
    # 计算原图四个角的位置坐标
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    
    # 计算旋转后的图像宽度和高度
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # 调整旋转矩阵的平移部分以将图像放在中心
    M[0, 2] += (new_w / 2) - cX
    M[1, 2] += (new_h / 2) - cY

    # 执行仿射变换（旋转）
    rotated_img = cv2.warpAffine(img, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    
    return rotated_img

def draw_red_dot(img, x, y, size):
    # 定义红色 (B, G, R)
    red_color = (0, 0, 255)
    
    # 使用 cv2.circle 在指定位置画红色的圆点
    cv2.circle(img, (x, y), size, red_color, thickness=-1)  # thickness=-1 表示填充整个圆
    
    return img
