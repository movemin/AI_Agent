import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key = os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3.5-flash"

# 도구: 우리가 짠 평범한 파이썬 함수
def add(a: float, b: float) -> float:
    """두 숫자를 더한다."""
    return a + b

# LLM에게 "이런 도구가 있다"고 알려주는 설명서
add_tool = types.Tool(function_declarations = [
    types.FunctionDeclaration(
        name = "add",
        description = "두 숫자를 더한다.",
        parameters = {
            "type": "object",
            "properties": {
                "a": {"type": "number"},
                "b": {"type": "number"}
            },
            "required": ["a", "b"]
        },
    )
])

def ask(question: str):
    response = client.models.generate_content(
        model = MODEL_NAME,
        contents = question,
        config = types.GenerateContentConfig(
            tools = [add_tool],
            # 자동 실행을 끈다: LLM이 "요청한" 하는 걸 직접 보기 위해서다
            automatic_function_calling = types.AutomaticFunctionCallingConfig(disable = True),
        )
    )
    part = response.candidates[0].content.parts[0]
    if part.function_call:
        print("LLM의 요청:", part.function_call.name, dict(part.function_call.args))
    else:
        print("LLM의 직접 답변:", response.text)

ask("안녕, 오늘 기분 어때?")
ask("1234 더하기 5678은 얼마야?")