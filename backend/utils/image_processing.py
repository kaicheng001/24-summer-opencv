import cv2
import numpy as np
import os

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
    if not os.path.exists(background_path):
        raise FileNotFoundError(f"Background image not found at {background_path}")
    
    background = cv2.imread(background_path)
    background = cv2.resize(background, (image.shape[1], image.shape[0]))

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    mask_inv = cv2.bitwise_not(mask)

    fg = cv2.bitwise_and(image, image, mask=mask_inv)
    bg = cv2.bitwise_and(background, background, mask=mask)
    
    combined_image = cv2.add(fg, bg)
    return combined_image
