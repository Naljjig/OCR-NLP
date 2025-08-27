import google.generativeai as genai
from PIL import Image

# Gemini API 키 설정
genai.configure(api_key=" ")

# 모델 로드 (이미지 입력을 지원하는 모델 사용)
model = genai.GenerativeModel("gemini-1.5-flash-8b")

# 이미지 파일 불러오기
image_path = "/Users/jincheol/Download/test1.png"
image = Image.open(image_path)

# 프롬프트와 이미지 함께 입력
prompt = """
            이미지를 분석하여 일정에 기록할 수 있도록 일정 제목, 날짜, 시간과 같은 일정 정보를 JSON 형식으로 추출해주세요.
            반환되는 날짜는 반드시 "YYYY.MM.DD" 형식으로, 시간은 "HH:MM" (24시간제) 형식으로 통일해주세요.
            만약 날짜나 시간 정보가 명확하지 않다면, 해당 필드는 "Null"로 설정해주세요.
            여러 날짜와 시간이 나타난다면, 가장 이른 날짜와 시간을 기준으로 표시해주세요.

            텍스트: $text

            JSON 형식 예시:
            {
              "original_text": "전체 텍스트",
              "schedule_info": {
                "event_title": "이벤트 제목",
                "date": "2024-12-25",
                "time": "14:00"
              }
            }
        """

# 프롬프트와 이미지 함께 입력
response = model.generate_content(
    [  {"text": prompt},    image])

# 응답 출력
print(response.text)
