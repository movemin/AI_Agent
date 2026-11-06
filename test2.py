import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("GENINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

history = []

system = "한국말하는 트럼프처럼 얘기해줘."

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

print(chat("내 이름은 제이슨이야. 잘 부탁해."))
print(chat("내 이름은 뭐라고?"))