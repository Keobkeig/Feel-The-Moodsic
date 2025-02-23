import numpy as np
import cv2
import scipy.spatial

# Emotion colors in BGR format with more distinct colors
EMOTION_COLORS = {
    # Joy family (upper right quadrant) - Vibrant yellows and oranges
    "orange": [255, 165, 0],
    "blue": [0, 0, 255],
    "bluegreen": [0, 165, 255],
    "green": [0, 205, 0],
    "red": [255, 0, 0],
    "yellow": [255, 255, 0],
    "purple": [128, 0, 128],
    "neutral": [255, 241, 224]
}

# Emotion positions with wider distribution
EMOTION_POSITIONS = {
    "orange": [0.6, 0.6],
    "blue": [-0.6, 0.6],
    "bluegreen": [0.5, 0.4],
    "green": [0.4, 0.5],
    "red": [-0.6, -0.6],
    "yellow": [0.3, 0.3],
    "purple": [-0.5, -0.4],
    "neutral": [0.0, 0.0],
}

def get_color_for_point(point_coords, emotions):
    """
    Compute an RGB color value for a point in the (-1, 1) 2D plane through interpolation.
    
    Args:
        point_coords: [x, y] coordinates of the point
        emotions: dictionary containing emotion names as keys and their positions
    """
    color = np.array([0.0, 0.0, 0.0])
    positions = np.array(list(EMOTION_POSITIONS.values()))
    distances = scipy.spatial.distance.cdist([point_coords], positions)[0]
    
    weights = 1 / (distances + 0.1)
    for emotion, weight in zip(EMOTION_COLORS.values(), weights):
        color += (np.array(emotion) * weight)
    color /= (np.sum(weights))
    
    sum_color = np.sum(color)
    required_sum_color = 600.0
    if color.max() * (required_sum_color/sum_color) <= 255:
        color *= (required_sum_color/sum_color)
    else:
        color *= (255/(color.max()))
    return color

def create_2d_color_map(emotions, height, width):
    """
    Create a colormap by interpolating RGB color values for emotions.
    
    Args:
        emotions: dictionary containing emotion names as keys and their positions
        height: height of the output image
        width: width of the output image
    """
    rgb = np.zeros((height, width, 3)).astype("uint8")
    c_x = int(width / 2)
    c_y = int(height / 2)
    step = 5
    win_size = int((step-1) / 2)
    
    for emotion, position in EMOTION_POSITIONS.items():
        y = c_y - int(position[1] * height / 2)
        x = c_x + int(position[0] * width / 2)
        rgb[y, x] = EMOTION_COLORS[emotion]
    
    # Interpolate colors
    for y in range(win_size, height - win_size, step):
        for x in range(win_size, width - win_size, step):
            x_real = (x - width / 2) / (width / 2)
            y_real = (height / 2 - y ) / (height / 2)
            color = get_color_for_point([x_real, y_real], emotions)
            rgb[y - win_size - 1 : y + win_size + 1,
                x - win_size - 1 : x + win_size + 1] = color
    
    bgr = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)
    return bgr

if __name__ == "__main__":
    bgr = create_2d_color_map(EMOTION_POSITIONS, 400, 400)
    
    height, width = bgr.shape[:2]
    cv2.line(bgr, (width//2, 0), (width//2, height), (128, 128, 128), 1)  
    cv2.line(bgr, (0, height//2), (width, height//2), (128, 128, 128), 1) 
    
    # Display
    cv2.imshow('Emotion Color Space', bgr)
    