import os
import re  # 찾기 및 바꾸기 기능
from dotenv import load_dotenv
from google import genai
from google.genai import types
import requests


# 안키 서버 주소
url = 'http://localhost:8765'

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash"

JLPT = "N2"
TARGET = "회화"

system = f"""
너는 자막 번역기다.
주어진 텍스트의 한자 옆에 후리가나를 넣고, `\t` 간격으로 2열에 한글 뜻을 적어라.
[규칙]
1. 절대 인사말, 설명, 부연 설명을 출력하지 마라.
2. 오직 '일본어(후리가나)\t한국어 뜻' 형태만 출력하라.
3. 숫자로만 이루어진 줄이나 화자 정보는 무시하라.
4. {JLPT}의 레벨과 {TARGET}의 목적에 맞게 번역해라.
"""

# chat_session = client.chats.create(
#     model=MODEL_NAME,
#     config=types.GenerateContentConfig(system_instruction=system)
# )

# def clean_srt(srt_text: str) -> list:
#     """SRT에서 시간 태그를 지우고 순수 텍스트를 리스트로 반환합니다."""
#     text = re.sub(r'^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n', '', srt_text, flags=re.MULTILINE)
#     text = re.sub(r'<[^>]+>', '', text)
#     return [line.strip() for line in text.split('\n') if line.strip()]


# # --- 실행부 ---
# print("1. 파일을 읽고 있습니다.")
with open("output.txt", "r", encoding="utf-8") as file:  # metante.srt
    raw_subtitle = file.read()

print("2. 자막의 숫자와 시간을 지우는 중입니다 (전처리).")
# cleaned_lines = clean_srt(raw_subtitle)

# print("3. AI에게 한 번에 번역을 요청합니다. 시간이 조금 걸릴 수 있습니다.")
# response = chat_session.send_message(raw_subtitle)
# result = response.text.strip()

# print("4. 변환 완료! .txt 파일로 저장합니다.")
# with open("output.txt", "w", encoding="utf-8") as output_file:
#     output_file.write(result)

# print("[안내] 모든 작업이 끝났습니다. output.txt 파일을 확인하세요.")

for card in raw_subtitle.split('\n'):  # 반복 대상 나중에 바꾸기
    result = card.split("\t")
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": "명탐정 코난 실험",
                "modelName": "명탐정 코난",  # 영문판 안키를 쓰신다면 "Basic"
                "fields": {
                    "예문(일본어)": result[0].strip(),
                    "예문(한국어)": result[-1].strip()
                },
                "options": {
                    "allowDuplicate": False  # 중복된 카드가 있으면 안키가 알아서 추가를 거부하게 만듭니다.
                },
                "tags": [
                    "자막변환", "파이썬자동화"  # 안키에서 카드를 쉽게 찾기 위한 태그 (선택 사항)
                ]
            }
        }
    }
    response = requests.post(url, json=payload).json()
    # 안키 서버가 에러를 뱉었는지 확인
    if response.get("error"):
        print(f"❌ 실패 [{result[0][:10]}...]: {response['error']}")
    else:
        print(f"✅ 성공 [{result[0][:10]}...]")


# print(response)