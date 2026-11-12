import pymupdf
import os

# pdf가 있는 경로
pdf_file_path = "chap04/data/AI-Agents-ko.pdf"

# pdf 읽기
doc = pymupdf.open(pdf_file_path)

# 헤더와 푸터의 높이
header_height = 80
footer_height = 80

# 축출할 총 pdf 텍스트를 저장하는 변수
full_text = ''


# 문서 페이지 반복
for page in doc:

    # 페이지 크기 가져오기
    rect = page.rect

    # 헤더
    header = page.get_text(clip = (0, 0, rect.width, header_height))

    # 푸터
    footer = page.get_text(clip = (0, rect.height - footer_height, rect.width, rect.height))

    # 페이지 텍스트 추출
    text = page.get_text(clip = (0, header_height, rect.width, rect.height - footer_height))

    # 텍스트 이어 붙이기
    full_text += text + '\n---------------------------------------------------\n'


# 상대경로 축출
pdf_file_name = os.path.basename(pdf_file_path)

# 확장자 제거
pdf_file_name = os.path.splitext(pdf_file_name)[0]

# 축출한 텍스트를 저장할 경로 저장
txt_file_path = f"chap04/output/{pdf_file_name}_with_preprocessing.txt"

# 텍스트를 뽑아 변수에 저장한 경로에 작성
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(full_text) 