import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

history = []

system = "내가 자막 파일을 주면 한자 옆에 후리가나를 넣어주고, `\t` 간격으로 2열에 한글 뜻을 적어주셈. 그 외에 쓸데없는 글 예를 들어 숫자나 누가 말하는 정보인지 대한 텍스트는 제거해줘."""

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

with open("metante.srt", "r") as file:
    subtitle = file.read() 

print(chat(f"{subtitle}"))
