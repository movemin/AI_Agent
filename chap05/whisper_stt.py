import os
import torch
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


# 자신이 설치한 위치 환경변수 등록
os.environ["PATH"] += os.pathsep + r"~/home/movemin/myproject/ffmpeg-2026-11-11-git-23c4540053-full_build"

def whisper_stt(
    audio_file_path: str,
    output_file_path: str = "./output.csv"
):
    """받아쓰기 기능"""
    
    # GPU 사용 가능 여부 확인
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model_id = "openai/whisper-small"

    # Whisper 모델 로드
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage = True,
        use_safetensors = True
    )
    model.to(device)

    # 오디오 전처리기 및 토크나이저 로드
    processor = AutoProcessor.from_pretrained(model_id)

    # 음성 인식 파이프라인 생성
    pipe = pipeline(
        "automatic-speech-recognition",
        model = model,
        tokenizer = processor.tokenizer,
        feature_extractor = processor.feature_extractor,
        torch_dtype = torch_dtype,
        device = device,

        
        return_timestamps = True,  # 파일을 청크 단위로 나누고 청크 시간을 각각 기록, 청크별로 타임스탬프를 반환
        chunk_length_s = 10,       # 10초 단위로 음성 분할, 입력 오디오를 10초씩 나누기
        stride_length_s = 2,       # 청크 경계의 앞뒤 5초 문맥 활용, 청크가 2초씩 겹치도록 나누기
    )

    # dataset = load_dataset("distil-whisper/librispeech_long", "clean", split = "validation")
    # sample = dataset[0]["audio"]
    result = pipe(audio_file_path)
    df = whisper_to_dataframe(result, output_file_path)

    return result, df

def whisper_to_dataframe(result, output_file_path):
    """판다스 데이터프레임 형태로 저장하는 기능"""

    # chunk를 CVS 파일로 저장
    start_end_text = []

    for chunk in result["chunks"]:
        start = chunk["timestamp"][0]
        end = chunk["timestamp"][1]
        text = chunk["text"]
        start_end_text.append([start, end, text])

    df = pd.DataFrame(start_end_text, columns = ["start", "end", "text"])
    df.to_csv("lsy_audio_2023_58s.csv", index = False, sep = "|")

    return df

if __name__ == '__main__':
    result, df = whisper_stt(
        "./chap05/audio/싼기타_비싼기타.mp3",
        "./chap05/audio/싼기타_비싼기타.csv",
    )

    print(df)