# 로컬 한국어 음성인식 (녹음 → 텍스트)

인터넷·API·계정 없이 **이 PC 안에서만** 녹음 파일을 텍스트로 바꿉니다.
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) (MIT) 기반, CPU 전용.

## 쓰는 법

**가장 쉬운 방법** — 녹음 파일을 `변환.bat` 위로 드래그&드롭.

**명령줄**

```powershell
.\.venv\Scripts\python.exe transcribe.py "녹음.m4a"
.\.venv\Scripts\python.exe transcribe.py 녹음폴더\ --out 결과\
```

원본 옆에 세 개가 생깁니다.

| 파일 | 용도 |
|---|---|
| `녹음.txt` | 문단으로 정리된 순수 텍스트 (문서화용) |
| `녹음.timestamped.md` | 줄마다 `0:03:21` 시각 (원본 대조용) |
| `녹음.srt` | 자막 |

mp3 · m4a · wav · flac · ogg · opus · mp4 · mkv · mov 등 대부분 읽습니다 (ffmpeg 설치 불필요).

## 옵션

```
--model    tiny / base / small / medium / large-v3-turbo(기본) / large-v3
--lang     기본 ko, `auto` 로 자동감지
--out      출력 폴더 (기본: 원본과 같은 위치)
--prompt   "오르카, 정회광, KPI"  ← 고유명사를 미리 알려주면 인식률이 올라갑니다
--threads  CPU 스레드 수 (기본: 자동)
--no-vad   무음 구간 자동 제거 끄기
--force    이미 결과가 있어도 다시 변환
```

## 모델 고르기 (이 PC = 8코어 CPU 기준)

| 모델 | 1시간 녹음 예상 | 비고 |
|---|---|---|
| `small` | 약 5~10분 | 초벌 확인용 |
| `medium` | 약 15~25분 | |
| `large-v3-turbo` | 약 15~25분 | **기본값.** 정확도/속도 균형 최고 |
| `large-v3` | 약 40~60분 | 제일 정확, 제일 느림 |

모델은 처음 쓸 때 한 번만 자동 다운로드되어 `%USERPROFILE%\.cache\huggingface` 에 저장됩니다.

## 인식률 올리는 팁

- `--prompt` 에 회의에 나오는 사람 이름·회사명·전문용어를 넣어주세요. 체감 차이가 큽니다.
- 녹음이 아주 조용하거나 잡음이 많으면 `--no-vad` 를 한번 시도해 보세요.
- 결과 `.txt` 를 Claude에 넘기면 요약·회의록 정리까지 됩니다 (클로바노트의 요약 기능 대체).

## 재설치

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install faster-whisper
```
