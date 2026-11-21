# 필요한 라이브러리들을 05-2절에서 만든 코드에서 가져와 임포트합니다.
import os
import torch
import pandas as pd
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline


# 자신이 설치한 위치 환경변수 등록
os.environ["PATH"] += os.pathsep + r"~/home/movemin/myproject/ffmpeg-2026-11-11-git-23c4540053-full_build"

# 받아쓰기 기능
def whisper_stt(audio_file_path: str, output_file_path: str = "./output.csv"):
    """음성 파일 경로를 넣으면 결과가 output_file_path에 CSV 형식으로 저장됩니다."""
    
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

# 판다스 데이터프레임 형태로 저장하는 기능
def whisper_to_dataframe(result, output_file_path):
    """위스퍼 모델을 이용해 얻은 결과를 CSV 파일로 저장"""

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

# 매개변수로 입출력할 파일 경로 추가
def speaker_diarization(audio_file_path: str, output_rttm_file_path: str, output_csv_file_path: str):
    
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-community-1", token = os.getenv("gpt-text-to-image"))

    # CUDA를 사용할 수 있다면 CUDA를 사용하도록 설정
    if torch.cuda.is_available():
        pipeline.to(torch.device("cuda"))
        print('cuda is available')
    else:
        print('cuda is not available')
    diarization_pipeline = pipeline(audio_file_path)   # 여러 파이프라인이 있으므로 가독성을 높이기 위해 pipeline -> diarization_pipeline

    # dump the diarization output to disk using RTTM format
    with open(output_rttm_file_path, "w", encoding='utf-8') as rttm:
        diarization_pipeline.speaker_diarization.write_rttm(rttm)

    # 판다스 데이터프레임으로 변환
    df_rttm = pd.read_csv(
        output_rttm_file_path,
        sep = ' ',
        header = None,
        names = ['type', 'file', 'chnl', 'start', 'duration', 'C1', 'C2', 'speaker_id', 'C3', 'C4']
        )

    df_rttm['end'] = df_rttm['start'] + df_rttm['duration']

    # speaker_id를 기반으로 화자별로 구간 나누기
    df_rttm["number"] = None
    df_rttm.at[0, "number"] = 0

    for i in range(1, len(df_rttm)):
        if df_rttm.at[i, "speaker_id"] != df_rttm.at[i - 1, "speaker_id"]:
            df_rttm.at[i, "number"] = df_rttm.at[i - 1, "number"] + 1
        else:
            df_rttm.at[i, "number"] = df_rttm.at[i - 1, "number"]

    df_rttm_grouped = df_rttm.groupby("number").agg(
        start = pd.NamedAgg(column = 'start', aggfunc = 'min'),
        end = pd.NamedAgg(column = 'end', aggfunc = 'max'),
        speaker_id = pd.NamedAgg(column = 'speaker_id', aggfunc = 'first')
    )

    df_rttm_grouped["duration"] = df_rttm_grouped["end"] - df_rttm_grouped["start"]

    df_rttm_grouped.to_csv(
        output_csv_file_path,
        index = False,  # 인덱스는 저장하지 않음
        encoding = 'utf-8'
    )
    return df_rttm_grouped

# 시간대별로 화자가 분리된 결과에 STT 결과 텍스트 할당하기
def stt_to_rttm(
    audio_file_path: str,
    stt_output_file_path: str,
    rttm_file_path: str,
    rttm_csv_file_path: str,
    final_output_csv_file_path: str
    ):

    # stt_to_rttm 함수는 whisper_stt 함수와 speaker_diarization 함수를 실행하여 결과를 받아 옵니다.
    result, df_stt = whisper_stt(
        audio_file_path,
        stt_output_file_path
    )

    df_rttm = speaker_diarization(
        audio_file_path,
        rttm_file_path,
        rttm_csv_file_path
    )

    df_rttm["text"] = ""  # 그 후 가져온 시간대별로 어느 화자가 발언했는지 정리된 df_rttm에 "text"라는 빈 열을 추가하고 위스퍼 모델로 받아쓴 텍스트를 채웁니다. 중요한 부분은 적절한 행 찾기

    for i_stt, row_stt in df_stt.iterrows():
        overlap_dict = {}
        for i_rttm, row_rttm in df_rttm.iterrows():

            # df_stt행과 df_rttm 행이 겹치는 시간을 각각 계산해서 가장 많이 겹치는 행에 텍스트를 추가
            # ex) 겹치는 시간이 0초라면 해당 문장을 건너뜁니다.
            overlap = max(0, min(row_stt["end"], row_rttm["end"]) - max(row_stt["start"], row_rttm["start"]))
            overlap_dict[i_rttm] = overlap

        max_overlap = max(overlap_dict.values())
        max_overlap_idx = max(overlap_dict, key = overlap_dict.get)

        if max_overlap > 0:
            df_rttm.at[max_overlap_idx, "text"] += row_stt["text"] + "\n"

    # 결과는 지정된 결로에 저장됩니다.
    df_rttm.to_csv(
        final_output_csv_file_path,
        index = False,  # 인덱스는 저장하지 않음
        sep = '|',
        encoding = 'utf-8'
    )
    return df_rttm

if __name__ == '__main__':
    audio_file_path = "./chap05/audio/싼기타_비싼기타.wav"
    stt_output_file_path = "./chap05/audio/싼기타_비싼기타.csv"
    rttm_file_path = "./chap05/audio/싼기타_비싼기타.rttm"
    rttm_csv_file_path = "./chap05/audio/싼기타_비싼기타_rttm.csv"
    final_csv_file_path = "./chap05/audio/싼기타_비싼기타_final.csv"
    
    # result, df = whisper_stt(
    #     "./chap05/audio/싼기타_비싼기타.mp3",
    #     "./chap05/audio/싼기타_비싼기타.csv",
    # )

    # df_rttm = speaker_diarization(
    #     audio_file_path,
    #     rttm_file_path,
    #     rttm_csv_file_path
    # )
    # print(df_rttm)

    df_rttm = stt_to_rttm(
        audio_file_path,
        stt_output_file_path,
        rttm_file_path,
        rttm_csv_file_path,
        final_csv_file_path
    )

    print(df_rttm)