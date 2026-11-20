import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
EMBED_MODEL = "gemini-embedding-001"

result = client.models.embed_content(
    model = EMBED_MODEL,
    contents = "수강신청 언제 해요?"
)
vec = result.embeddings[0].values

print("벡터 길이:", len(vec))
print("앞 5개 숫자:", vec[:5])