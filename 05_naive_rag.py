import os
import math
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "gemini-3.5-flash"
EMBED_MODEL = "gemini-embedding-001" # 임베딩 전용 모델 (아래 주의사항 참고)

# 1. 인덱싱: 문서를 조각(chunk)으로 나눈다. 여기서는 FAQ 한 쌍이 한 조각
chunks = [
    "Q: 수강신청 기간은 언제인가요? A: 매 학기 시작 2주 전, 월요일부터 금요일까지입니다.",
    "Q: 휴학 신청은 어디서 하나요? A: 학교 포털의 '학적' 메뉴에서 신청합니다.",
    "Q: 도서관 이용 시간은? A: 평일 오전 9시부터 오후 9시까지입니다.",
    "Q: 장학금 신청 방법은? A: 학교 포털의 '장학금' 메뉴를 통해 신청합니다.",
]

def embed(text: str) -> list[float]:
    """글을 숫자 리스트(벡터)로 바꾼다."""
    result = client.models.embed_content(model=EMBED_MODEL, contents=text)
    return result.embeddings[0].values

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """두 벡터가 얼마나 비슷한지 (1에 가까울수록 비슷)"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    return dot / (norm_a * norm_b)

# 모든 조각을 미리 벡터로 바꿔 저장한다 (이게 "벡터 저장소"의 정체다)
index = [(chunk, embed(chunk)) for chunk in chunks]

def retrieve(question: str, top_k: int = 2, threshold: float = 0.7) -> list[str]:
    # 2. 검색: 질문과 가장 비슷한 조각 top_k개를 찾는다.
    q_vec = embed(question)
    scored = [(cosine_similarity(q_vec, vec), chunk) for chunk, vec in index]
    scored.sort(reverse=True) # 내림차순 정렬

    # 기준값 이상인 것만 남긴다 (출력과 반환 모두에 적용)
    selected = [(score, chunk) for score, chunk in scored[:top_k] if score > threshold]

    # 검색 결과를 눈으로 확인할 수 있게 점수도 출력한다
    for score, chunk in selected:
        print(f"    [유사도 {score:.3f}] {chunk[:30]}")
    if not selected:
        print("    (기준을 넘는 조각 없음)")
    return [chunk for score, chunk in selected]

def rag_answer(question: str) -> str:
    """3. 생성: 찾은 조각만 붙여서 LLM에게 답하게 한다."""
    print(f"\n질문: {question}")
    found = retrieve(question)
    if not found:
        return "FAQ에 없는 내용입니다."
    context = "\n".join(found)
    system = f"""너는 학교 FAQ 안내 챗봇이다.
아래 [참고 자료]만 근거로 답해라.
자료에 없으면 추측하지 말고 "FAQ에 없는 내용입니다. 학교 사무실에 문의하세요."라고 답해라.

[참고자료]
{context}
""" 
    response = client.models.generate_content(
        model = MODEL_NAME,
        contents = question,
        config = types.GenerateContentConfig(system_instruction=system)
    )
    return response.text

# 테스트: 말을 바꾼 질문 / 없는 질문
print(rag_answer("수강 등록은 언제 하는 거야?"))
print(rag_answer("학식 메뉴가 뭐야?"))

# for m in client.models.list():
#     if "embed" in m.name:
#         print(m.name)