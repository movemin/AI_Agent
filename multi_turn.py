from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("CHATGPT_API_KEY")

client = OpenAI(api_key = api_key)

MODEL_NAME = "gpt-4o"

def get_ai_response(messages):
    response = client.chat.completions.create(
        model = MODEL_NAME,
        temperature = 0.9,
        messages = messages,
    )
    return response.choices[0].message.content

messages = [
        {"role": "system", "content": "너는 사용자를 도와주는 사용자야."},
]

while True:
    user_input = input("사용자: ")

    
    if user_input == "exit":
        break

    messages.append({"role": "user", "content": user_input})
    ai_response = get_ai_response(messages)
    messages.append({"role": "assistant", "content": ai_response})
    print("AI: " + ai_response)