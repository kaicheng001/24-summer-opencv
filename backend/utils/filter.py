import cv2


# 热色调滤镜
def apply_hot_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_HOT)

# 冷色调滤镜
def apply_cool_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_COOL)

# 彩虹滤镜
def apply_rainbow_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_RAINBOW)

# 粉色滤镜
def apply_pink_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_PINK)

# 春季滤镜
def apply_spring_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_SPRING)

# 夏季滤镜
def apply_summer_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_SUMMER)

# 冬季滤镜
def apply_winter_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_WINTER)

# 海洋滤镜
def apply_ocean_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_OCEAN)

# 秋季滤镜
def apply_autumn_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_AUTUMN)

# 骨滤镜
def apply_bone_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_BONE)

# 喷气式滤镜
def apply_jet_filter(image):
    return cv2.applyColorMap(image, cv2.COLORMAP_JET)

# HSV 滤镜
def apply_hsv_filter(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 卡通效果
def cartoonize_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 7)
    color = cv2.bilateralFilter(image, 9, 300, 300)
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

# 草图效果
def sketch_image(image):
    # 将图像转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用中值滤波器进行模糊处理，去除噪点
    blurred = cv2.medianBlur(gray, 5)

    # 使用自适应阈值来检测边缘
    edges = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 7)

    return edges
