import argparse
import os
import subprocess
from collections.abc import Set


def sizeof_fmt(num, suffix="B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def run_ffmpeg(
    input_file: str,
    *,
    start_time: str,
    end_time: str | None = None,
    audio_tracks: Set[int] | None = None,
    scale: int | None = None,
    crf: int | None = None,
    preset="medium",
) -> None:
    output_file = os.path.splitext(input_file)[0] + "_cut.mp4"

    cmd = ["ffmpeg", "-y", "-i", input_file, "-ss", start_time]

    if end_time:
        cmd += ["-to", end_time]

    if audio_tracks:
        audio_inputs = "".join(f"[0:a:{t}]" for t in audio_tracks)

        # 비디오 필터
        vf_filter = (
            f"[0:v:0]scale={scale}:-2[vout]" if scale else "[0:v:0]copy[vout]"
        )

        # 오디오 믹스
        filter_complex = (
            f"{vf_filter};{audio_inputs}amix=inputs={len(audio_tracks)}[aout]"
        )

        if crf is not None:
            cmd += [
                "-crf",
                f"{crf}",
            ]

        cmd += [
            "-filter_complex",
            filter_complex,
            "-map",
            "[vout]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            output_file,
        ]

    else:
        # 기본 오디오 사용
        vf_option = []
        if scale:
            vf_option.append(f"scale={scale}:-2")
        vf_str = ",".join(vf_option) if vf_option else None

        if vf_str:
            cmd += ["-vf", vf_str]

        if crf is not None:
            cmd += [
                "-crf",
                f"{crf}",
            ]

        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            preset,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            output_file,
        ]

    print("실행할 명령어:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print(
        f"완료: {output_file}\n동영상 크기: {sizeof_fmt(os.path.getsize(output_file))}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FFmpeg 동영상 자르기 + 오디오 병합 + 압축"
    )
    parser.add_argument("video", help="동영상 경로")
    parser.add_argument("start", help="시작 시간 (HH:MM:SS)")
    parser.add_argument("--end", help="끝 시간 (HH:MM:SS)", default=None)
    parser.add_argument(
        "--audio",
        help="오디오 트랙 번호들 (예: 0,1)",
        default="",
    )
    parser.add_argument(
        "--scale", help="가로 해상도 지정 (예: 1280)", default=None
    )
    parser.add_argument(
        "--crf",
        help="Constant Rate Factor. Push the compression level further by increasing the CRF value (24 ~ 30 recommended)",
        default=None,
    )
    parser.add_argument(
        "--preset",
        help="프리셋 설정 (기본값: medium)",
        choices=(
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        ),
        default="medium",
    )

    args = parser.parse_args()
    input_file: str = args.video
    start_time: str = args.start
    end_time: str = args.end
    audio_tracks: Set[int] | None = set(map(int, args.audio.split(",")))
    scale: int | None = int(args.scale) if args.scale is not None else None
    crf: int | None = int(args.crf) if args.crf is not None else None
    preset: str = args.preset

    run_ffmpeg(
        input_file=input_file,
        start_time=start_time,
        end_time=end_time,
        audio_tracks=audio_tracks,
        scale=scale,
        crf=crf,
        preset=preset,
    )
