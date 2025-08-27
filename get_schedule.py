import requests
import json
from paddleocr import PaddleOCR
import base64
import os
import shutil

# PaddleOCR로 이미지에서 텍스트 추출
# def extract_text_from_image(image_path):
#     ocr = PaddleOCR(use_angle_cls=True, lang='korean')  # 한글 지원
#     result = ocr.ocr(image_path, cls=True)
    
#     extracted_text = ""
#     for line in result[0]:  # OCR 결과에서 텍스트 부분만 추출
#         extracted_text += line[1][0] + " "  # 텍스트만 추출
#     return extracted_text.strip()

def extract_text_from_image_google_vision(image_path, api_key):
    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

    # 이미지 파일 읽기
    # with open(image_path, "rb") as image_file:
    #     image_content = image_file.read()
    with open(image_path, "rb") as image_file:
        image_content = base64.b64encode(image_file.read()).decode('utf-8')

    # 요청 페이로드 생성
    payload = {
        "requests": [
            {
                "image": {"content": image_content},  # 이미지 바이너리 인코딩
                "features": [{"type": "TEXT_DETECTION"}]
            }
        ]
    }

    headers = {"Content-Type": "application/json"}

    # Google Vision API 호출
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        try:
            # 텍스트만 추출
            texts = result["responses"][0]["textAnnotations"]
            return texts[0]["description"].strip() if texts else ""
        except Exception as e:
            print("결과 파싱 중 오류:", e)
            return ""
    else:
        print("API 호출 오류:", response.status_code, response.text)
        return ""
    
# Gemini API를 활용해 일정 정보 추출
def extract_schedule_with_gemini(api_key, text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    아래 텍스트에서 일정에 기록할 수 있도록 일정 제목, 날짜, 시간과 같은 일정 정보를 JSON 형식으로 추출해주세요.
    날짜,시간 정보가 텍스트에 명시되어 있지 않으면 "time" 필드는 "Null"으로 설정해주세요.
    형식 예시: {{"event_title": "이벤트 제목", "date": "2024-12-25", "time": "Null"}}

    텍스트: {text}  
    """
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(url, headers=headers, json=payload, params={"key": api_key})
    
    if response.status_code == 200:
        try:
            response_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(response_text)  # JSON 형식으로 파싱
        except Exception as e:
            print("결과 파싱 중 오류 발생:", e)
            return None
    else:
        print("API 호출 오류:", response.status_code, response.text)
        return None

# 데이터셋 생성
# def create_dataset(image_path, gemini_api_key, dataset_path):
# def create_dataset(image_path, gemini_api_key, dataset_path):
#     # Step 1: 이미지에서 텍스트 추출
#     # extracted_text = extract_text_from_image(image_path)
#     extracted_text = extract_text_from_image_google_vision(image_path, gemini_api_key)
#     # print("추출된 텍스트:\n", extracted_text)
    
#     # Step 2: Gemini API로 일정 정보 추출
#     schedule_info = extract_schedule_with_gemini(gemini_api_key, extracted_text)
    
#     # Step 3: 데이터셋 저장
#     if schedule_info:
#         dataset_entry = {
#             "original_text": extracted_text,
#             "schedule_info": schedule_info
#         }
        
#         # 파일이 존재하지 않으면 생성
#         with open(dataset_path, 'a', encoding='utf-8') as f:
#             if f.tell() == 0:  # 파일이 비어 있는 경우
#                 f.write('')  # 빈 파일 생성
        
#         with open(dataset_path, 'a', encoding='utf-8') as f:
#             json.dump(dataset_entry, f, ensure_ascii=False)
#             f.write('\n')  # 각 엔트리를 새로운 줄에 저장
#         print("데이터셋에 저장 완료:", dataset_entry)
#     else:
#         print("일정 정보 추출 실패")
def create_dataset_for_all_images(image_dir, gemini_api_key, dataset_path):
    no_schedule_dir = os.path.join(image_dir, "일정 없음")
    os.makedirs(no_schedule_dir, exist_ok=True)

    for filename in os.listdir(image_dir):
        image_path = os.path.join(image_dir, filename)
        
        if not os.path.isfile(image_path):
            continue

        extracted_text = extract_text_from_image_google_vision(image_path, gemini_api_key)
        schedule_info = extract_schedule_with_gemini(gemini_api_key, extracted_text)
        
        if schedule_info and not (schedule_info.get("date") == "Null" and schedule_info.get("time") == "Null"):
            dataset_entry = {
                "original_text": extracted_text,
                "schedule_info": schedule_info
            }
            with open(dataset_path, 'a', encoding='utf-8') as f:
                json.dump(dataset_entry, f, ensure_ascii=False)
                f.write('\n')
            print("데이터셋에 저장 완료:", dataset_entry)
        else:
            shutil.move(image_path, os.path.join(no_schedule_dir, filename))
            print(f"일정 정보 추출 실패: {filename}을(를) '일정 없음' 폴더로 이동")

# 실행 예시
if __name__ == "__main__":
    image_dir = "Dataset//dataset"  # 이미지 파일 경로
    gemini_api_key = " "  # Gemini API 키 입력
    dataset_path = "Dataset/testset"  # 데이터셋 파일 경로
    create_dataset_for_all_images(image_dir, gemini_api_key, dataset_path)
