import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

# def ask_llm(prompt: str):
#     response = client.models.generate_content(
#         model=MODEL_NAME, contents=prompt)
#     return response.text

# # 1단계: 기억 없는 호출 (매번 새 대화)
# print("======첫번째 대답======")
# print(ask_llm("내 이름은 민수야. 기억해줘."))
# print("======두번째 대답======")
# print(ask_llm("내 이름이 뭐라고 했지?"))

# 대화 기록: 우리 코드가 들고 있는 "기억"
history = []

def chat(user_text: str) -> str:
    # 1) 사용자 말을 기록에 추가
    history.append(types.Content(role="user", parts=[types.Part(text=user_text)]))

    # 2) 기록 전체를 LLM에 보낸다
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=history,
    )
    answer = response.text

    # 3) AI 답변도 기록에 추가 (Gemini에서는 role이 "model")
    history.append(types.Content(role="model", parts=[types.Part(text=answer)]))
    return answer

print("======첫번째 대답======")
print(chat("내 이름은 민수야. 기억해줘."))
print("======두번째 대답======")
print(chat("내 이름이 뭐라고 했지?"))
print("======세번째 대답======")
print(f"\n기록 길이: {len(history)}개")