import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

history = []

system = "너는 개발자임. 내가 코드 주면 파이썬 문법대로 출력해주셈."

def chat(prompt: str) -> str:
    history.append(types.Content(role = "user", parts = [types.Part(text = prompt)]))
    response = client.models.generate_content(
        model = MODEL_NAME,
        contents = history,
        config = types.GenerateContentConfig(system_instruction=system)
    )

    answer = response.text
    history.append(types.Content(role = "model", parts = [types.Part(text = answer)]))

    return answer

print(chat("hello 문자열 출력 코드 주라."))
print(chat("내가 뭐 부탁했지?"))