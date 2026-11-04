import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  # .env 파일에서 키 읽기
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 모델명은 여기 한 곳에서만 관리한다
MODEL_NAME = "gemini-3.5-flash"

def ask_llm(prompt: str) -> str:
    """LLM 호출을 함수 하나로 감싼다."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    return response.text

print(ask_llm("머신러닝과 딥러닝의 차이를 한 문장으로 설명해줘."))