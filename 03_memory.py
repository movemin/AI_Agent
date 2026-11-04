import os
from dotenv import load_dotenv
from google import genai
# from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"
def ask_llm(prompt: str):
    response = client.models.generate_content(
        model=MODEL_NAME, contents=prompt)
    return response.text

# 1단계: 기억 없는 호출 (매번 새 대화)
print("======첫번째 대답======")
print(ask_llm("내 이름은 민수야. 기억해줘."))
print("======두번째 대답======")
print(ask_llm("내 이름이 뭐라고 했지?"))