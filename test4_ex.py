import os
import re  # 찾기 및 바꾸기 기능
from dotenv import load_dotenv
from google import genai
from google.genai import types

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

chat_session = client.chats.create(
    model=MODEL_NAME,
    config=types.GenerateContentConfig(system_instruction=system)
)

def clean_srt(srt_text: str) -> list:
    """SRT에서 시간 태그를 지우고 순수 텍스트를 리스트로 반환합니다."""
    text = re.sub(r'^\d+\s*\n\d{2}:\d{2}:\d{2},\d{3}\s*-->\s*\d{2}:\d{2}:\d{2},\d{3}\s*\n', '', srt_text, flags=re.MULTILINE)
    text = re.sub(r'<[^>]+>', '', text)
    return [line.strip() for line in text.split('\n') if line.strip()]

def process_in_chunks(lines: list, chunk_size: int = 50):
    """자막을 50줄씩 쪼개서 번역하고 즉시 파일에 이어붙여 씁니다."""
    total_chunks = (len(lines) + chunk_size - 1) // chunk_size
    output_filename = "output.txt"
    
    if os.path.exists(output_filename):
        os.remove(output_filename)

    print(f"총 {len(lines)}줄의 자막을 {total_chunks}번으로 나누어 처리를 시작합니다...\n")

    for i in range(total_chunks):
        chunk_lines = lines[i * chunk_size : (i + 1) * chunk_size]
        chunk_text = "\n".join(chunk_lines)
        
        print(f"[{i+1}/{total_chunks}] 파트 변환 중... ", end="", flush=True)
        
        try:
            response = chat_session.send_message(chunk_text)
            result = response.text.strip()
            
            with open(output_filename, "a", encoding="utf-8") as output_file:
                output_file.write(result + "\n")
            
            print("완료!")
        except Exception as e:
            print(f"오류 발생: {e}")
            
    print(f"\n[안내] 파일 작성이 완료되었습니다. '{output_filename}'을 확인하세요.")

# --- 실행부 ---
print("파일을 읽고 있습니다.")
with open("metante.srt", "r", encoding="utf-8") as file:
    raw_subtitle = file.read() 

print("AI 분석 및 전처리가 시작되었습니다.")
cleaned_lines = clean_srt(raw_subtitle)

# 청킹 및 변환 실행
process_in_chunks(cleaned_lines, chunk_size=50)