from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
    ColorClip,
    AudioFileClip,
    VideoClip,
    CompositeAudioClip
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

    # ───────────────────────────────────────────────
    # AUDIO 1.2x SPEED (VERSION SAFE)
    # ───────────────────────────────────────────────
    audio = AudioFileClip(audio_path)
    speed_factor = 1.2
    original_duration = audio.duration

    audio = audio.fl_time(lambda t: t * speed_factor, apply_to=['audio'])
    audio = audio.set_duration(original_duration / speed_factor)

    duration = audio.duration
    print(f"[DEBUG] Audio duration after speed: {duration:.2f}s")

    # ───────────────────────────────────────────────
    # SLIDESHOW
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
            clips.append(
                ColorClip(
                    size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT),
                    color=(10, 10, 30)
                ).set_duration(dur_per_img)
            )

    slideshow = concatenate_videoclips(clips, method="compose")

    # ───────────────────────────────────────────────
    # HEADER
    # ───────────────────────────────────────────────
    header_bg = (
        ColorClip(size=(config.VIDEO_WIDTH, 90), color=(0, 0, 0))
        .set_opacity(0.6)
        .set_duration(duration)
    )

    headline_clip = TextClip(
        headline,
        fontsize=50,
        color='white',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 80, None),
        method='caption',
        align='center'
    ).set_position(('center', 20)).set_duration(duration)

    header = CompositeVideoClip([header_bg, headline_clip])\
        .set_position(("center", "top"))

    # ───────────────────────────────────────────────
    # SUBTITLES (YELLOW ACTIVE STYLE)
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
            color='yellow',
            stroke_color='black',
            stroke_width=3,
            font='Arial-Bold',
            size=(config.VIDEO_WIDTH - 120, None),
            method='caption',
            align='center'
        )

    subtitle_clip = SubtitlesClip(subs, subtitle_maker)\
        .set_position(('center', config.VIDEO_HEIGHT - 220))

    # ───────────────────────────────────────────────
    # PROGRESS BAR (CLEAR & VISIBLE)
    # ───────────────────────────────────────────────
    bar_height = 14
    bar_y = config.VIDEO_HEIGHT - 40

    progress_bg = (
        ColorClip(
            size=(config.VIDEO_WIDTH, bar_height),
            color=(60, 60, 60)
        )
        .set_duration(duration)
        .set_position(("left", bar_y))
    )

    def make_progress_frame(t):
        progress = max(0, min(1, t / duration))
        width = int(config.VIDEO_WIDTH * progress)

        frame = np.zeros(
            (bar_height, config.VIDEO_WIDTH, 3),
            dtype=np.uint8
        )

        if width > 0:
            frame[:, :width] = (255, 0, 0)

        return frame

    progress_fill = VideoClip(make_progress_frame, duration=duration)\
        .set_position(("left", bar_y))

    # ───────────────────────────────────────────────
    # INITIAL HOOK
    # ───────────────────────────────────────────────
    initial_hook = TextClip(
        hook,
        fontsize=90,
        color='yellow',
        stroke_color='black',
        stroke_width=6,
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 80, None),
        method='caption'
    ).set_position('center').set_duration(5)

    initial_hook = initial_hook.resize(lambda t: 1 + 0.15 * t)

    # ───────────────────────────────────────────────
    # BACKGROUND MUSIC
    # ───────────────────────────────────────────────
    try:
        bg_music = AudioFileClip("background_music.mp3")\
            .volumex(0.15)\
            .audio_loop(duration=duration)

        final_audio = CompositeAudioClip([audio, bg_music])
        print("[INFO] Background music added")

    except Exception:
        final_audio = audio
        print("[INFO] No background_music.mp3 found")

    # ───────────────────────────────────────────────
    # END SCREEN
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

    end_screen = CompositeVideoClip([end_bg, subscribe_text])\
        .set_start(end_start)

    # ───────────────────────────────────────────────
    # FINAL COMPOSITION
    # ───────────────────────────────────────────────
    final_video = CompositeVideoClip([
        slideshow,
        header,
        subtitle_clip,
        progress_bg,
        progress_fill,
        initial_hook,
        end_screen
    ]).set_audio(final_audio).set_duration(duration)

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

    print(f"[SUCCESS] Video saved: {output_path}")

    return output_path