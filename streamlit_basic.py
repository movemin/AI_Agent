import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# 환경변수 파일을 쓰게 해주는 메서드 호출
load_dotenv()

# 사이드바 생성
with st.sidebar:
    openai_api_key = os.getenv("CHATGPT_API_KEY")

    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"
    "[Chat GPT OpenAI API key 발급](https://platform.openai.com/account/api-keys)"
    "[소스 코드](https://github.com/streamlit/llm-examples/blob/main/Chatbot.py)"
    "[PyMuPDF 가이드 문서 웹 페이지](https://pypi.org/project/PyMuPDF)"


# 모델 설정
MODEL_NAME = "gpt-4o"
st.title("Chatbot")

# 스트림릿에서 사용자의 세션 상태를 관리하는 기능
# 사용자가 상호 작용하는 동안 그 상태를 유지하고 업데이트할 수 있다.
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "무엇을 도와드릴까요?"}]

# 대화 기록을 웹 브라우저에 출력하는 부분
# st.chat_message는 스트림릿의 채팅 인터페이스에서 메시지를 출력하는 용도
# 메시지 역할은 assistant, user
# 각 요소는 .write()로 출력
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ai모델 불러오는 파이썬 메서드.
def get_ai_response(messages):
    """프롬프트를 넣고 호출하면 GPT의 답변이 문자열 형태로 나옵니다."""
    response = client.chat.completions.create(
        model = MODEL_NAME,
        temperature = 0.9,
        messages = messages,
    )
    return response.choices[0].message.content

    

# st.chat_input: 파이썬에서의 input을 생각하면 된다
if prompt := st.chat_input():
    if not openai_api_key:

        # Streamlit 스크립트 실행을 중단함
        st.info("Open API key를 연결해주세요.")
        st.stop()
    # api 연결
    client = OpenAI(api_key = openai_api_key)

    # 사용자 메시지를 대화 기록에 추가하여 멀티턴 대화에 활용
    st.session_state.messages.append({"role": "user", "content": prompt})

    # gui에 출력
    st.chat_message("user").write(prompt)

    # ai 답변 저장
    ai_response = get_ai_response(st.session_state.messages)

    # ai 답변 멀티턴
    st.session_state.messages.append({"role": "assistant", "content": ai_response})

    # gui에 출력
    st.chat_message("assistant").write(ai_response)