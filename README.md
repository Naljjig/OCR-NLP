# OCR-NLP
image ocr + NLP

## 
1. 이미지 크롤링을 통해서 데이터셋 수집
2. image_organize.py를 활용하여 중복 이미지 처리 및 정렬 
3. Gemini api를 활용하여 이미지에서 schedule title, date, time 정보 추출  truth dataset 제작
4. OCR_NLP.ipynb 내에서  이미지 수신 및 처리 활용 
    easyocr -> text 추출
    koBart  -> schedule title 생성



rerequisites

Python 3.8+
Required libraries: easyocr, transformers (for KoBART), google-generativeai (for Gemini API).
