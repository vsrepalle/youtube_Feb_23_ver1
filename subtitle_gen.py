# Subtitle generator 
"""Very basic subtitle generator — equal duration splits"""

from pathlib import Path

def create_simple_srt(text: str, duration_sec: float, out_path: str = "temp/subtitles.srt") -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return ""

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    time_per_line = duration_sec / max(1, len(lines))

    with open(path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines, 1):
            start_sec = (i-1) * time_per_line
            end_sec   = i * time_per_line

            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = int(t % 60)
                ms = int((t % 1) * 1000)
                return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

            f.write(f"{i}\n")
            f.write(f"{fmt(start_sec)} --> {fmt(end_sec)}\n")
            f.write(f"{line}\n\n")

    return str(path)