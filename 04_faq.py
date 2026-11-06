import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"

# FAQ 문서 (실제로는 파일에서 읽지만, 지금은 코드에 넣는다)
FAQ = """
Q: 수강신청 기간은 언제인가요?
A: 매 학기 시작 2주 전, 월요일부터 금요일까지 입니다.

Q: 휴학 신청은 어디서 하나요?
A: 학교 포털의 '학적' 메뉴에서 신청합니다.

Q: 도서관 이용 시간은?
A: 평일 오전 9시부터 오후 9시까지입니다.

Q: 장학금 신청 방법은?
A: 학교 포털의 '장학금' 메뉴를 통해 신청합니다.
"""

# 시스템 프롬프트: FAQ 안에서만 답하게 가둔다
SYSTEM = f"""너는 학교 FAQ 안내 챗봇이다.
아래 FAQ 내용만 근거로 답해라.
FAQ에 없는 질문이면 추측하지 말고 "FAQ에 없는 내용입니다. 학과 사무실에 문의하세요."라고 답해라.

[FAQ]
{FAQ}
"""

def ask_faq(question: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=question,
        config=types.GenerateContentConfig(system_instruction=SYSTEM)
    )
    return response.text

# 테스트 3종: 있는 질문 / 말만 다르게 한 질문 / 없는 질문
print(ask_faq("수강신청 언제 해요?"))
print(ask_faq("휴학하려면 어디로 가야 돼?"))
print(ask_faq("학식 메뉴가 뭐야?"))     # FAQ에 없음. 모른다고 해야 정답
print(ask_faq("장학금은 어떻게 신청해?"))