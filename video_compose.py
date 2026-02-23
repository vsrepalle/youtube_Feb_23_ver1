"""Video composition for YouTube Shorts - 9:16 vertical format
   - Header: only headline, small top bar, no overlap
   - Subtitles: sentence-wise, scrolling, current sentence yellow
   - Progress bar: visible filling bar
   - Initial hook: big animated text at start
   - Subscribe hook: end screen CTA
   - Background music: low volume loop
"""

from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
    ColorClip,
    AudioFileClip,
    VideoClip,
    vfx,
    afx
)

from moviepy.video.tools.subtitles import SubtitlesClip

import config
from pathlib import Path
import time
import numpy as np


def make_short_video(
    images: list[Path],
    audio_path: str,
    english_text: str,
    headline: str,
    hook: str,
    subscribe_hook: str,
    output_path: str = "output/final_short.mp4"
) -> str:

    start_total = time.time()
    print("[TIMER] Video composition started")

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    audio = AudioFileClip(audio_path)
    duration = audio.duration
    print(f"[DEBUG] Audio duration: {duration:.2f}s")

    if duration < 5:
        raise ValueError("Audio too short")

    # ───────────────────────────────────────────────
    # Slideshow
    # ───────────────────────────────────────────────
    clips = []
    dur_per_img = duration / max(1, len(images))

    for img_path in images:
        try:
            clip = (
                ImageClip(str(img_path))
                .set_duration(dur_per_img)
                .resize(width=config.VIDEO_WIDTH)
                .set_position(("center", "center"))
            )
            clips.append(clip)
        except Exception:
            black = (
                ColorClip(
                    size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT),
                    color=(10, 10, 30)
                )
                .set_duration(dur_per_img)
            )
            clips.append(black)

    slideshow = concatenate_videoclips(clips, method="compose")

    # ───────────────────────────────────────────────
    # Initial hook
    # ───────────────────────────────────────────────
    initial_hook = TextClip(
        hook,
        fontsize=100,
        color='yellow',
        stroke_color='black',
        stroke_width=6,
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 100, None),
        method='caption'
    ).set_position('center').set_duration(5)

    initial_hook = initial_hook.resize(lambda t: 1 + 0.15 * t)
    initial_hook = initial_hook.set_opacity(1)

    # ───────────────────────────────────────────────
    # Header
    # ───────────────────────────────────────────────
    header_height = 100

    header_bg = (
        ColorClip(size=(config.VIDEO_WIDTH, header_height), color=(0, 0, 0))
        .set_opacity(0.6)
        .set_duration(duration)
    )

    headline_clip = TextClip(
        headline,
        fontsize=55,
        color='white',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 100, None),
        method='caption',
        align='center'
    ).set_position(('center', 25)).set_duration(duration)

    header = CompositeVideoClip(
        [header_bg, headline_clip]
    ).set_position(("center", "top"))

    # ───────────────────────────────────────────────
    # Subtitles
    # ───────────────────────────────────────────────
    sentences = [s.strip() for s in english_text.split('\n') if s.strip()]
    if not sentences:
        sentences = ["No text available"]

    subs = []
    t = 0
    step = duration / len(sentences)

    for sent in sentences:
        end = min(t + step, duration)
        subs.append(((t, end), sent))
        t = end

    def subtitle_maker(txt):
        return TextClip(
            txt,
            fontsize=60,
            color='white',
            stroke_color='black',
            stroke_width=3,
            font='Arial',
            size=(config.VIDEO_WIDTH - 120, None),
            method='caption',
            align='center'
        )

    subtitle_clip = (
        SubtitlesClip(subs, subtitle_maker)
        .set_position(('center', config.VIDEO_HEIGHT - 250))
    )

    # ───────────────────────────────────────────────
    # ✅ FIXED Progress Bar (No resize lambda)
    # ───────────────────────────────────────────────
    bar_height = 12
    bar_y = config.VIDEO_HEIGHT - bar_height - 250

    progress_bg = (
        ColorClip(
            size=(config.VIDEO_WIDTH, bar_height),
            color=(80, 80, 80)
        )
        .set_duration(duration)
        .set_position(("center", bar_y))
    )

    def make_progress_frame(t):
        progress = max(0, min(1, t / duration))
        width = int(config.VIDEO_WIDTH * progress)

        frame = np.zeros(
            (bar_height, config.VIDEO_WIDTH, 3),
            dtype=np.uint8
        )

        if width > 0:
            frame[:, :width] = (220, 40, 40)

        return frame

    progress_fill = (
        VideoClip(make_progress_frame, duration=duration)
        .set_position(("left", bar_y))
    )

    # ───────────────────────────────────────────────
    # Background music
    # ───────────────────────────────────────────────
    final_audio = audio

    try:
        bg_music = AudioFileClip("background_music.mp3")
        bg_music = bg_music.volumex(0.15).audio_loop(duration=duration)
        final_audio = audio.volumex(1.0).audio_fadein(2).audio_fadeout(2)
        final_audio = final_audio.set_duration(duration)
        final_audio = final_audio.set_audio(bg_music)
        print("[INFO] Background music added")
    except Exception:
        print("[INFO] No background_music.mp3 found → using voice only")

    # ───────────────────────────────────────────────
    # End screen
    # ───────────────────────────────────────────────
    end_duration = 5
    end_start = duration - end_duration

    end_bg = (
        ColorClip(
            size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT),
            color=(0, 0, 0)
        )
        .set_opacity(0.7)
        .set_duration(end_duration)
    )

    subscribe_text = TextClip(
        subscribe_hook,
        fontsize=70,
        color='yellow',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 100, None),
        method='caption'
    ).set_position('center').set_duration(end_duration)

    end_screen = (
        CompositeVideoClip([end_bg, subscribe_text])
        .set_start(end_start)
    )

    # ───────────────────────────────────────────────
    # Final composition
    # ───────────────────────────────────────────────
    final_video = (
        CompositeVideoClip([
            slideshow,
            header,
            progress_bg,
            progress_fill,
            subtitle_clip,
            initial_hook.set_duration(5),
            end_screen
        ])
        .set_audio(audio)
        .set_duration(duration)
    )

    print("[DEBUG] Writing final video...")

    final_video.write_videofile(
        output_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        logger=None
    )

    total_time = time.time() - start_total
    min_sec = divmod(total_time, 60)

    print(f"[SUCCESS] Video saved: {output_path}")
    print(f"[TIMER] Total: {int(min_sec[0])} min {int(min_sec[1])} sec")

    return output_path