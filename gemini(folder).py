import google.generativeai as genai
from PIL import Image
import os
import json
import shutil
import re

def clean_response_text(response_text):
    """
    응답 텍스트에서 ```json, ``` 등을 제거하고 JSON 문자열만 남김
    """
    # 정규표현식으로 ```로 감싼 부분 제거
    cleaned_text = re.sub(r"```(?:json)?\n?", "", response_text)
    cleaned_text = cleaned_text.strip()  # 불필요한 앞뒤 공백 제거
    return cleaned_text

# Gemini API 키 설정
genai.configure(api_key=" ")

# 모델 로드 (이미지 입력을 지원하는 모델 사용)
model = genai.GenerativeModel("gemini-1.5-flash")

# 프롬프트 정의
prompt_template = """
이 이미지를 분석하여 다음과 같은 정보를 추출해주세요.

1. 이미지에서 추출한 전체 텍스트를 반환해주세요.
2. 일정에 기록할 수 있는 정보(일정 제목, 날짜, 시간)를 JSON 형식으로 반환해주세요. 
   만약 텍스트에서 일정을 찾을 수 없다면 모든 필드(event_title, date, time)를 "Null"로 설정해주세요.

JSON 형식 예시:
{
  "original_text": "이미지에서 추출된 전체 텍스트",
  "schedule_info": {
    "event_title": "Null",
    "date": "Null",
    "time": "Null"
  }
}
"""

def save_to_jsonl(output_path, entry):
    with open(output_path, 'a', encoding='utf-8') as f:
        json.dump(entry, f, ensure_ascii=False)
        f.write('\n')  # 각 JSON 객체를 새로운 줄에 기록


# 폴더 내 모든 이미지 처리
def process_images_in_folder(folder_path, output_path):
    # dataset = []  # 데이터셋을 저장할 리스트
    ended_folder = os.path.join(folder_path, "ended")
    os.makedirs(ended_folder, exist_ok=True)  # 'ended' 폴더가 없으면 생성
    err_folder = os.path.join(folder_path, "err")
    os.makedirs(err_folder, exist_ok=True)  # 'ended' 폴더가 없으면 생성
    count = 0
    # 폴더 내 모든 이미지 파일을 순회
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):  # 이미지 확장자 확인
            count+=1
            image_path = os.path.join(folder_path, filename)
            print(f"처리 중: {image_path}")
            
            try:
                # 이미지 파일 불러오기
                image = Image.open(image_path)

                # 프롬프트 생성 및 API 호출
                response = model.generate_content([
                    {"text": prompt_template},
                    image
                ])

                # 응답 파싱
                #response_t = response.text
                response_text = response.text
                # response_text = response_t.strip('```json\n').strip('```')
                # JSON 파싱
                # JSON 데이터 추출
                try:
                    # 정규식을 사용하여 '''json과 ''' 사이의 텍스트 추출
                    match = re.search(r"```json\n(.*?)```", response_text, re.DOTALL)
                    if match:
                        json_text = match.group(1)  # 추출된 JSON 텍스트
                        parsed_response = json.loads(json_text)  # JSON 파싱
                    else:
                        raise ValueError("JSON 형식의 데이터가 응답에 포함되어 있지 않습니다.")

                except json.JSONDecodeError as e:
                    print(f"JSON 파싱 오류: {e}")
                    print("텍스트 확인:", response_text)
                    shutil.move(image_path, os.path.join(err_folder, filename))
                    continue
                    #break
                

                # 데이터셋 항목 생성
                dataset_entry = {
                    "filename": filename,
                    "original_text": parsed_response.get("original_text", ""),
                    "schedule_info": parsed_response.get("schedule_info", {})
                }  
                
                # dataset.append(dataset_entry)
                save_to_jsonl(output_path, dataset_entry)
                # 이미지 처리 완료 후 'ended' 폴더로 이동
                shutil.move(image_path, os.path.join(ended_folder, filename))

            except Exception as e:
                print(f"오류 발생: {e}")
                shutil.move(image_path, os.path.join(err_folder, filename))
                continue

            print(count)

    print(f"데이터셋 저장 완료: {output_path}")

# 실행 예시
if __name__ == "__main__":
    folder_path = "/Users/jincheol/Desktop/종합 설계/Dataset/dataset"  # 이미지가 저장된 폴더 경로
    output_path = "/Users/jincheol/Desktop/종합 설계/Dataset/dataset/correct_set"  # 데이터셋 파일 저장 경로
    process_images_in_folder(folder_path, output_path)
