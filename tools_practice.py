"""
사용자가 '10 과 20을 더해줘' 라고 입력하면 
LLM이 스스로 add() 함수를 선택하고 파이썬이 실제 계산을 실행하는 실습
"""

# 컴퓨터가 이해할 수 있는 언어 => json
import json
import os                       # api 키를 직접 입력하는 대신 운영체제의 환경변수를 빼내기 위해
from dotenv import load_dotenv  # 파이썬 패키지를 받아 파이썬 코드로 운영체제 환경변수 등록
from openai import OpenAI       # GPT

# 파이썬 환경변수 패키지 사용 선언
load_dotenv()

# os에서 환경변수를 불러와 api키 불러오기
api_key = os.getenv("CHATGPT_API_KEY")

# api키 등록
client = OpenAI(api_key = api_key)

# 1. 도구 만들기
def add(a, b):
    """더하기 기능"""
    return a + b


# 2. LLM에게 도구 설명하기
tools = [
    {
        "type": "function",
        "function": {
            "name": "add",
            
            # LLM이 사용자 요청의 의미와 도구 설명을 참고해
            # 어떤 도구를 사용할지 판단한다.
            "description": "두 숫자를 더한다.",  # LLM이 desciption을 보고 사용자가 입력한 프롬프트와 비교하여 판단.
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        }
    }
]

# 3. 사용자 질문
messages = [
    {"role": "user", "content": "10과 20을 더해줘"}
]

# 4. LLM이 도구 선택
response = client.chat.completions.create(
    model = "gpt-4o",
    messages = messages,
    tools = tools
)

message = response.choices[0].message

# 5. 파이썬이 실제 도구 실행
if message.tool_calls:
    messages.append(message)

    for tool_call in message.tool_calls:
        args = json.loads(tool_call.function.arguments)

        if tool_call.function.name == "add":
            result = add(**args)

            print(f"LLM이 선택한 도구: {tool_call.function.name}")
            print(f"도구 실행 결과: {result}")

            # LLM이 요청한 도구의 실행 결과를 대화 기록에 추가한다.
            # 다음 API 호출에서 이 기록을 전달하면
            # LLM이 실행 결과를 확인할 수 있다.
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })

    # 6. 도구 실행 결과를 LLM에게 전달  ->  실행 결과를 LLM에게 전달해 최종 답변 생성
    final = client.chat.completions.create(
        model = "gpt-4o",
        messages = messages
    )

    print(f"AI 최종 답변: {final.choices[0].message.content}")



# json
# 서로 다른 프로그램이 데이터를 주고받기 위해 사용하는 표준적인 텍스트 형식
# 각각의 프로그램은 사용언어가 다르기 때문에 프로그램과 프로그램간의 통일적인 언어가 필요함

# 그렇다면 json.loads()는 왜 사용할까?
# tool_call.function.arguments는 JSON 형식의 문자열(str)
# LLM이 반환한 JSON 문자열 : arguments = '{"a": 10, "b": 20}'
# print(type(arguments))
# <class 'str'>
# -> 문자열 그대로는 키워드 인자에 전달 불가

# 해결
# args = json.loads(arguments)
# print(args) # {'a': 10, 'b': 20} -> 문자열이 아닌 파이썬의 딕셔너리 형태로 반환함
# print(type(args)) # <class 'dict'>

# load
#      함수	            역할
# json.loads()	JSON 문자열 → 파이썬 객체
# json.dumps()	파이썬 객체 → JSON 문자열
# json.load()	JSON 파일 → 파이썬 객체
# json.dump()	파이썬 객체 → JSON 파일