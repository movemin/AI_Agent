import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key = os.getenv("CHATGPT_API_KEY"))

MODEL_NAME = "gpt-4o"
response = client.chat.completions.create(
    model = MODEL_NAME,
    temperature = 0.9,
    messages = [
        {"role": "system", "content": "너는 명탐정 코난에 나오는 골룸보 반장이야. 그 인물의 말투에 맞게 답변을 해줘."},
        {"role": "user", "content": "코난은 어디있나요?"},
    ]
)

print("---")

print(response.choices[0].message.content)