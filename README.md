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
--beam     빔 크기 (기본 5). 1로 낮추면 눈에 띄게 빨라지고 정확도는 조금 내려갑니다
--threads  CPU 스레드 수 (기본: 자동)
--no-vad   무음 구간 자동 제거 끄기
--force    이미 결과가 있어도 다시 변환
```

## 속도 — 이 PC(8코어 CPU, GPU 없음) 실측

2분 54초짜리 한국어 음성으로 잰 값입니다. GPU가 없어서 **이게 이 도구의 병목**입니다.

| 모델 | 2분 54초 처리 | 실시간 대비 | 1시간 녹음 환산 |
|---|---|---|---|
| `small` | 1.4분 | 0.5배 | **약 30분** |
| `medium` | (small과 turbo 사이) | | 약 50분 |
| `large-v3-turbo` (기본) | 3.3분 | 1.1배 | **약 70분** |
| `large-v3` | 훨씬 느림 | | 몇 시간 |

즉 **1시간 회의 녹음이면 기본 설정으로 1시간쯤 걸립니다.** 급할 때는:

- `--model small` → 4배쯤 빠름. 초벌 확인용으로는 충분합니다.
- `--beam 1` → 어느 모델에서든 추가로 빨라집니다.
- 밤에 걸어두고 자는 것도 방법입니다. 폴더를 통째로 넘기면 순서대로 다 처리합니다.

## 인식률 올리는 팁

- `--prompt` 에 회의에 나오는 사람 이름·회사명·전문용어를 넣어주세요. 체감 차이가 큽니다.
- 녹음이 아주 조용하거나 잡음이 많으면 `--no-vad` 를 한번 시도해 보세요.
- 결과 `.txt` 를 Claude에 넘기면 요약·회의록 정리까지 됩니다 (클로바노트의 요약 기능 대체).

## 모델 캐시 위치

모델은 처음 쓸 때 한 번만 자동 다운로드됩니다 (`large-v3-turbo` 약 1.6GB).
이 PC는 C: 용량이 빠듯해서 사용자 환경변수로 D:에 받도록 해뒀습니다.

```
HF_HOME = D:\orca\cache\huggingface
```

이 변수가 없으면 `%USERPROFILE%\.cache\huggingface` (= C 드라이브)에 쌓입니다.

## 재설치

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install faster-whisper
```
