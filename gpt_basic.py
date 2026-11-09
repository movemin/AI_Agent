import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key = os.getenv('CHATGPT_API_KEY')
)

MODEL_NAME = "gpt-4o"

response = client.chat.completions.create(
    model=MODEL_NAME,
    temperature=0.1,
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "2022년 월드컵 우승 팀은 어디야?"
        }
    ]
)

print(response)
print(response.choices[0].message.content)
