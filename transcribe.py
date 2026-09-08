#!/usr/bin/env python
"""로컬 한국어 음성인식 -> 텍스트 문서화 (faster-whisper, CPU 전용, 인터넷/API 불필요).

사용법:
    python transcribe.py 녹음.m4a
    python transcribe.py 폴더/ --model large-v3
    python transcribe.py *.mp4 --out 결과
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# 한글 콘솔(cp949)에서 표현 못 하는 문자가 섞여도 죽지 않도록.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(errors="replace")

MEDIA_EXT = {
    ".mp3", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".wma", ".aac", ".amr",
    ".mp4", ".mkv", ".mov", ".webm", ".avi", ".3gp",
}

# 문단 나누기 기준: 이 시간(초) 이상 말이 끊기거나, 문단이 이 길이를 넘으면 줄바꿈.
PARA_GAP_SEC = 2.0
PARA_MAX_CHARS = 300


def fmt_clock(seconds: float) -> str:
    """0:03:21 형태 (본문 타임스탬프용)."""
    s = int(seconds)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


def fmt_srt(seconds: float) -> str:
    """00:03:21,480 형태 (자막용)."""
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def collect_inputs(paths: list[str]) -> list[Path]:
    found: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            found += sorted(f for f in p.iterdir() if f.suffix.lower() in MEDIA_EXT)
        elif p.is_file():
            found.append(p)
        else:
            print(f"[건너뜀] 파일을 찾을 수 없음: {p}", file=sys.stderr)
    return found


def to_paragraphs(segments: list[tuple[float, float, str]]) -> list[str]:
    paras: list[str] = []
    buf: list[str] = []
    prev_end = None
    for start, _end, text in segments:
        gap = None if prev_end is None else start - prev_end
        too_long = sum(len(t) for t in buf) > PARA_MAX_CHARS
        if buf and ((gap is not None and gap >= PARA_GAP_SEC) or too_long):
            paras.append(" ".join(buf))
            buf = []
        buf.append(text)
        prev_end = _end
    if buf:
        paras.append(" ".join(buf))
    return paras


def write_outputs(src: Path, out_dir: Path, segments: list[tuple[float, float, str]]) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    written = []

    # 1) 읽기용 순수 텍스트
    txt = out_dir / f"{stem}.txt"
    txt.write_text("\n\n".join(to_paragraphs(segments)) + "\n", encoding="utf-8")
    written.append(txt)

    # 2) 타임스탬프 붙은 마크다운 (원본 확인용)
    md = out_dir / f"{stem}.timestamped.md"
    lines = [f"# {stem}", ""]
    lines += [f"`{fmt_clock(s)}` {text}" for s, _e, text in segments]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append(md)

    # 3) 자막
    srt = out_dir / f"{stem}.srt"
    blocks = [
        f"{i}\n{fmt_srt(s)} --> {fmt_srt(e)}\n{text}\n"
        for i, (s, e, text) in enumerate(segments, 1)
    ]
    srt.write_text("\n".join(blocks), encoding="utf-8")
    written.append(srt)

    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="로컬 음성인식 -> txt/md/srt")
    ap.add_argument("inputs", nargs="+", help="오디오/영상 파일 또는 폴더")
    ap.add_argument("--model", default="large-v3-turbo",
                    help="tiny/base/small/medium/large-v3/large-v3-turbo (기본: large-v3-turbo)")
    ap.add_argument("--lang", default="ko", help="언어 코드, auto 로 자동감지 (기본: ko)")
    ap.add_argument("--out", type=Path, default=None, help="출력 폴더 (기본: 원본과 같은 위치)")
    ap.add_argument("--compute-type", default="int8", help="int8 / int8_float32 / float32 (기본: int8)")
    ap.add_argument("--threads", type=int, default=0, help="CPU 스레드 수 (0=자동)")
    ap.add_argument("--beam", type=int, default=5,
                    help="빔 크기. 1로 낮추면 30%% 정도 빨라지고 정확도는 조금 내려갑니다 (기본: 5)")
    ap.add_argument("--prompt", default="", help="고유명사/용어를 미리 알려주면 인식률이 올라갑니다")
    ap.add_argument("--no-vad", action="store_true", help="무음 구간 제거(VAD) 끄기")
    ap.add_argument("--force", action="store_true", help="이미 결과가 있어도 다시 변환")
    args = ap.parse_args()

    files = collect_inputs(args.inputs)
    if not files:
        print("변환할 파일이 없습니다.", file=sys.stderr)
        return 1

    from faster_whisper import WhisperModel  # 임포트가 느려서 인자 검증 뒤에

    print(f"모델 로딩: {args.model} ({args.compute_type}, CPU) - 최초 1회는 다운로드가 있습니다")
    model = WhisperModel(
        args.model,
        device="cpu",
        compute_type=args.compute_type,
        cpu_threads=args.threads,
    )

    for src in files:
        out_dir = args.out or src.parent
        if not args.force and (out_dir / f"{src.stem}.txt").exists():
            print(f"[건너뜀] 이미 변환됨: {src.name}  (--force 로 재변환)")
            continue

        print(f"\n=== {src.name} ===")
        t0 = time.time()
        segments, info = model.transcribe(
            str(src),
            language=None if args.lang == "auto" else args.lang,
            initial_prompt=args.prompt or None,
            beam_size=args.beam,
            vad_filter=not args.no_vad,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,  # 긴 녹음에서 같은 문장 반복되는 것 방지
        )
        total = info.duration or 0.0
        print(f"길이 {fmt_clock(total)} / 감지 언어 {info.language} ({info.language_probability:.0%})")

        collected: list[tuple[float, float, str]] = []
        for seg in segments:  # 제너레이터라 여기서 실제 인식이 진행됩니다
            text = seg.text.strip()
            if not text:
                continue
            collected.append((seg.start, seg.end, text))
            elapsed = time.time() - t0
            pct = (seg.end / total * 100) if total else 0
            print(f"\r  {pct:5.1f}%  {fmt_clock(seg.end)}/{fmt_clock(total)}"
                  f"  (경과 {elapsed / 60:.1f}분)   ", end="", flush=True)
        print()

        if not collected:
            print("  인식된 음성이 없습니다.")
            continue

        for path in write_outputs(src, out_dir, collected):
            print(f"  -> {path}")
        print(f"  완료: {(time.time() - t0) / 60:.1f}분 소요")

    return 0


if __name__ == "__main__":
    sys.exit(main())
