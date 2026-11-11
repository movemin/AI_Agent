from openai import OpenAI
from dotenv import load_dotenv
import os
import pymupdf

load_dotenv()
api_key = os.getenv('CHATGPT_API_KEY')

def pdf_to_text(pdf_file_path: str):
    doc = pymupdf.open(pdf_file_path)

    header_height = 80
    footer_height = 80

    full_text = ''

    for page in doc:
        rect = page.rect

        header = page.get_text(clip = (0, 0, rect.width, header_height))
        footer = page.get_text(clip = (0, rect.height - footer_height, rect.width, rect.height))
        text = page.get_text(clip = (0, header_height, rect.width, rect.height - footer_height))

        full_text += text + '\n---------------------------------------------------\n'

    # 파일명만 축출  
    pdf_file_name = os.path.basename(pdf_file_path)

    # 확장자 제거
    pdf_file_name = os.path.splitext(pdf_file_name)[0]

    # 축출한 텍스트를 저장할 경로 저장
    txt_file_path = f"chap04/output/{pdf_file_name}_with_preprocessing.txt"

    # 텍스트를 뽑아 변수에 저장한 경로에 작성
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    return txt_file_path

def summarize_txt(file_path: str):
    client = OpenAI(api_key = api_key)

    with open(file_path, 'r', encoding = 'utf-8') as f:
        txt = f.read()

    system_prompt = f'''
    너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 의식과 주장을 파악하고, 주요 내용을 요약하라.

    작성해야 하는 포맷은 다음과 같다.

    # 제목
    
    ## 저자의 문제 의식 및 주장 (15문장 이내)

    ## 저자 소개


    =============== 이하 텍스트 ===============

    { txt }
    '''

    print(system_prompt)
    print("=======================================")

    response = client.chat.completions.create(
        model = 'gpt-4o',
        temperature = 0.1,
        messages = [
            {"role": "system", "content": system_prompt},
        ]
    )

    return response.choices[0].message.content

def summarize_pdf(pdf_file_path: str, output_file_path: str):
    txt_file_path = pdf_to_text(pdf_file_path)
    summary = summarize_txt(txt_file_path)

    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(summary)

if __name__ == '__main__':
    pdf_file_path = 'chap04/data/AI-Agents-ko.pdf'

    summarize_pdf(pdf_file_path, './chap04/output/crop_model_summary2.txt')