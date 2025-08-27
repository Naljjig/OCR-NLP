import os
import hashlib
from PIL import Image

def calculate_image_hash(image_path):
    """이미지의 해시 값을 계산합니다."""
    with Image.open(image_path) as img:
        # 이미지를 RGB로 변환하고 크기를 줄여서 해시 계산
        img = img.convert('RGB').resize((8, 8), Image.LANCZOS)
        pixels = list(img.getdata())
        avg_pixel = sum(pixels) / len(pixels)
        bits = ''.join(['1' if pixel > avg_pixel else '0' for pixel in pixels])
        hex_representation = '{:016x}'.format(int(bits, 2))
        return hex_representation

def rename_duplicate_images(folder_path):
    """폴더 내의 이미지를 비교하여 동일한 이미지를 이름을 바꿉니다."""
    image_hashes = {}
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            image_path = os.path.join(folder_path, filename)
            image_hash = calculate_image_hash(image_path)
            
            if image_hash in image_hashes:
                # 동일한 이미지가 이미 존재하는 경우
                base_name = image_hashes[image_hash]
                new_name = f"{base_name}_1.jpg"
                counter = 1
                while os.path.exists(os.path.join(folder_path, new_name)):
                    counter += 1
                    new_name = f"{base_name}_{counter}.jpg"
                os.rename(image_path, os.path.join(folder_path, new_name))
            else:
                # 새로운 이미지인 경우
                base_name = os.path.splitext(filename)[0]
                image_hashes[image_hash] = base_name

# 사용 예시
folder_path = '/Users/jincheol/Desktop/종합 설계/Dataset/정리'
rename_duplicate_images(folder_path)
