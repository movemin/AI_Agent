import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-3.5-flash"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM = "띠거운 술주정뱅이 아저씨처럼 대답해줘."
history = []

def ask_llm(prompt: str) -> str:
    history.append(types.Content(role="user", parts = [types.Part(text=prompt)]))
    response = client.models.generate_content(
        model=MODEL_NAME, 
        contents=history,
        config=types.GenerateContentConfig(system_instruction=SYSTEM)
    )
    answer = response.text
    history.append(types.Content(role="model", parts = [types.Part(text=answer)]))

    return answer


print(ask_llm("내 이름은 민수야. 잘 기억해."))

print(ask_llm("내 이름은 뭐지?"))