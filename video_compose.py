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
    print(f"[TIMER] Video composition started for: {headline}")

    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # ───────────────────────────────────────────────
    # AUDIO PROCESSING
    # ───────────────────────────────────────────────
    audio = AudioFileClip(audio_path)
    
    # Check if duration is valid, otherwise force read it
    if audio.duration is None:
        print("[ERROR] Could not read audio duration. Check if temp/audio.mp3 is valid.")
        # Fallback duration if metadata is missing (approximate words/sec)
        duration = len(english_text.split()) / 2.5 
    else:
        duration = audio.duration

    # Log the duration and warn if >60 seconds
    if duration > 60:
        print(f"⚠️  WARNING: Video duration is {duration:.2f}s (exceeds 60s YouTube Shorts limit)")
        print("   Video will still be created as Short format but may not be eligible for Shorts")
    
    speed_factor = 1.2
    # Apply speed change and explicitly set new duration to avoid NoneType errors
    audio = audio.fl_time(lambda t: speed_factor * t, apply_to=['audio'])
    duration = duration / speed_factor
    audio = audio.set_duration(duration)

    print(f"[DEBUG] Audio Duration: {duration:.2f}s")
    print(f"[DEBUG] Video Dimensions: {config.VIDEO_WIDTH}x{config.VIDEO_HEIGHT} (9:16 aspect ratio)")

    # ───────────────────────────────────────────────
    # SLIDESHOW GENERATION
    # ───────────────────────────────────────────────
    clips = []
    # Ensure at least one image exists to avoid division by zero
    num_images = max(1, len(images))
    dur_per_img = duration / num_images

    for img_path in images:
        try:
            clip = (
                ImageClip(str(img_path))
                .set_duration(dur_per_img)
                .resize(width=config.VIDEO_WIDTH)
                .set_position(("center", "center"))
            )
            clips.append(clip)
        except Exception as e:
            print(f"[WARN] Skipping bad image {img_path}: {e}")

    # Handle case where NO images were successfully loaded
    if not clips:
        clips.append(ColorClip(size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT), color=(20, 20, 40)).set_duration(duration))

    slideshow = concatenate_videoclips(clips, method="compose")

    # ───────────────────────────────────────────────
    # HEADER (Headline Overlay)
    # ───────────────────────────────────────────────
    header_bg = (
        ColorClip(size=(config.VIDEO_WIDTH, 110), color=(0, 0, 0))
        .set_opacity(0.7)
        .set_duration(duration)
    )

    headline_clip = TextClip(
        headline.upper(),
        fontsize=45,
        color='white',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 60, None),
        method='caption',
        align='center'
    ).set_position(('center', 25)).set_duration(duration)

    header = CompositeVideoClip([header_bg, headline_clip]).set_position(("center", "top"))

    # ───────────────────────────────────────────────
    # SUBTITLES
    # ───────────────────────────────────────────────
    lines = [line.strip() for line in english_text.split('.') if line.strip()]
    if not lines: lines = ["Generating content..."]

    subs = []
    t_cursor = 0
    step = duration / len(lines)

    for line in lines:
        end = min(t_cursor + step, duration)
        subs.append(((t_cursor, end), line))
        t_cursor = end

    def subtitle_maker(txt):
        return TextClip(
            txt,
            fontsize=55,
            color='yellow',
            stroke_color='black',
            stroke_width=2,
            font='Arial-Bold',
            size=(config.VIDEO_WIDTH - 100, None),
            method='caption',
            align='center'
        )

    subtitle_clip = SubtitlesClip(subs, subtitle_maker).set_position(('center', config.VIDEO_HEIGHT - 300))

    # ───────────────────────────────────────────────
    # PROGRESS BAR
    # ───────────────────────────────────────────────
    bar_h, bar_y = 10, config.VIDEO_HEIGHT - 10
    
    progress_bg = ColorClip(size=(config.VIDEO_WIDTH, bar_h), color=(50, 50, 50))\
                    .set_duration(duration).set_position(("left", bar_y))

    def make_progress_frame(t):
        progress_w = int(config.VIDEO_WIDTH * (t / duration))
        frame = np.zeros((bar_h, config.VIDEO_WIDTH, 3), dtype=np.uint8)
        if progress_w > 0:
            frame[:, :progress_w] = (255, 0, 0)
        return frame

    progress_fill = VideoClip(make_progress_frame, duration=duration).set_position(("left", bar_y))

    # ───────────────────────────────────────────────
    # INITIAL HOOK (Zoom effect for first 3 seconds)
    # ───────────────────────────────────────────────
    hook_dur = min(3.5, duration)
    initial_hook = TextClip(
        hook,
        fontsize=80,
        color='yellow',
        stroke_color='black',
        stroke_width=4,
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 100, None),
        method='caption'
    ).set_position('center').set_duration(hook_dur)
    
    initial_hook = initial_hook.resize(lambda t: 1 + 0.08 * t)

    # ───────────────────────────────────────────────
    # AUDIO FINAL MIX
    # ───────────────────────────────────────────────
    try:
        bg_music = AudioFileClip("background_music.mp3").volumex(0.12).audio_loop(duration=duration)
        final_audio = CompositeAudioClip([audio, bg_music])
    except:
        final_audio = audio

    # ───────────────────────────────────────────────
    # END SCREEN
    # ───────────────────────────────────────────────
    end_scr_dur = 4
    end_start_time = max(0, duration - end_scr_dur)

    end_bg = ColorClip(size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT), color=(0, 0, 0))\
                .set_opacity(0.85).set_duration(end_scr_dur)

    subscribe_text = TextClip(
        subscribe_hook,
        fontsize=60,
        color='white',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 120, None),
        method='caption'
    ).set_position('center').set_duration(end_scr_dur)

    end_screen = CompositeVideoClip([end_bg, subscribe_text]).set_start(end_start_time)

    # ───────────────────────────────────────────────
    # FINAL RENDER
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

    # Ensure video is in portrait orientation for Shorts
    if final_video.size[0] > final_video.size[1]:
        print("[WARNING] Video is landscape, rotating to portrait for Shorts format")
        final_video = final_video.resize(height=config.VIDEO_HEIGHT)
    
    final_video.write_videofile(
        output_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        threads=2, # Safer for local machines
        logger=None
    )

    # Final check
    import os
    file_size = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n[SUMMARY] Video created: {output_path}")
    print(f"[SUMMARY] Duration: {duration:.2f}s")
    print(f"[SUMMARY] Dimensions: {final_video.w}x{final_video.h}")
    print(f"[SUMMARY] File size: {file_size:.2f} MB")
    
    if duration > 60:
        print("[NOTE] Video exceeds 60s - will not be eligible for YouTube Shorts")

    return output_path