import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

def ask_llm(prompt: str, system: str = "") -> str:
    """system이 있으면 시스템 프롬프트로 전달한다."""
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system),
    )
    return response.text

question = "머신러닝이 뭐야?"

print("=== 시스템 프롬프트 없음 ===")
print(ask_llm(question))

print("\n===엄격한 선생님 역할===")
print(ask_llm(question, system="너는 냉정한 과외 선생님이다. 두 문장 이내로 답하고, 마지막에 학생에게 확인 질문을 하나 던져라."))