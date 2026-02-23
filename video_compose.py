"""Video composition for YouTube Shorts - 9:16 vertical format"""

from moviepy.editor import (
    TextClip,
    CompositeVideoClip,
    ImageClip,
    concatenate_videoclips,
    ColorClip,
    AudioFileClip
)
from moviepy.video.tools.subtitles import SubtitlesClip
import config
from pathlib import Path
import time

def make_short_video(
    images: list[Path],
    audio_path: str,
    english_text: str,
    headline: str,
    hook: str,
    output_path: str = "output/final_short.mp4"
) -> str:
    start_total = time.time()
    print("[TIMER] Video composition started")

    # Auto-create output directory
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"[DEBUG] Output directory ensured: {output_dir}")

    # Load audio
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    print(f"[DEBUG] Audio loaded. Duration: {duration:.2f} seconds")

    if duration < 1:
        raise ValueError("Audio file is too short or corrupted")

    # ───────────────────────────────────────────────
    # Slideshow (bottom 80%)
    # ───────────────────────────────────────────────
    header_height = config.HEADER_HEIGHT
    content_height = config.VIDEO_HEIGHT - header_height

    print(f"[DEBUG] Header height: {header_height}px, Content height: {content_height}px")

    clips = []
    duration_per_img = duration / max(1, len(images))

    for i, img_path in enumerate(images):
        print(f"[DEBUG] Loading image {i+1}/{len(images)}: {img_path.name}")
        try:
            clip = (ImageClip(str(img_path))
                    .set_duration(duration_per_img)
                    .resize(height=content_height)
                    .set_position(("center", header_height)))
            clips.append(clip)
        except Exception as e:
            print(f"[WARNING] Failed to load image {img_path}: {e} → using fallback")
            black = ColorClip(size=(config.VIDEO_WIDTH, content_height), color=(10,10,30))
            black = black.set_duration(duration_per_img)
            clips.append(black.set_position(("center", header_height)))

    slideshow = concatenate_videoclips(clips, method="compose")
    print("[DEBUG] Slideshow concatenated")

    # ───────────────────────────────────────────────
    # Header (top 20%)
    # ───────────────────────────────────────────────
    header_bg = ColorClip(
        size=(config.VIDEO_WIDTH, header_height),
        color=(20, 20, 60)
    ).set_duration(duration)

    headline_clip = TextClip(
        headline,
        fontsize=65,
        color='white',
        font='Arial-Bold',
        size=(config.VIDEO_WIDTH - 80, None),
        method='caption',
        align='center'
    ).set_position(('center', 30)).set_duration(duration)

    hook_clip = TextClip(
        hook,
        fontsize=48,
        color='yellow',
        font='Arial',
        size=(config.VIDEO_WIDTH - 120, None),
        method='caption',
        align='center'
    ).set_position(('center', headline_clip.h + 50)).set_duration(duration)

    header = CompositeVideoClip([header_bg, headline_clip, hook_clip])
    print("[DEBUG] Header composed")

    # ───────────────────────────────────────────────
    # Simple English subtitles
    # ───────────────────────────────────────────────
    print("[DEBUG] Generating subtitles...")
    def subtitle_maker(txt):
        return TextClip(txt, fontsize=50, color='white', stroke_color='black', stroke_width=2,
                        font='Arial', size=(config.VIDEO_WIDTH - 100, None), method='caption')

    sentences = [s.strip() for s in english_text.split('\n') if s.strip()]
    subs = []
    t = 0
    step = duration / max(1, len(sentences))
    for sent in sentences:
        subs.append(((t, t + step), sent))
        t += step

    subtitle_clip = SubtitlesClip(subs, subtitle_maker).set_position(('center', 'bottom'))
    print(f"[DEBUG] Created {len(subs)} subtitle segments")

    # ───────────────────────────────────────────────
    # Progress bar – position animation
    # ───────────────────────────────────────────────
    print("[DEBUG] Creating progress bar...")
    bar_height = 12
    bar_y = config.VIDEO_HEIGHT - bar_height

    progress_bg = ColorClip(
        size=(config.VIDEO_WIDTH, bar_height),
        color=(80, 80, 80)
    ).set_duration(duration).set_position(("center", bar_y))

    bar_width = config.VIDEO_WIDTH
    progress_fill = ColorClip(
        size=(bar_width, bar_height),
        color=(220, 40, 40)
    ).set_duration(duration).set_position(
        lambda t: (t / duration * (config.VIDEO_WIDTH - bar_width), bar_y)
    )

    # ───────────────────────────────────────────────
    # Final composition
    # ───────────────────────────────────────────────
    print("[DEBUG] Building final composite...")
    final_video = CompositeVideoClip([
        slideshow,
        header.set_position(("center", "top")),
        progress_bg,
        progress_fill,
        subtitle_clip
    ]).set_audio(audio).set_duration(duration)

    print("[DEBUG] Final composition ready. Writing file...")
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

    total_time = time.time() - start_total
    min_sec = divmod(total_time, 60)
    print(f"[TIMER] Total: {int(min_sec[0])} min {int(min_sec[1])} sec ({total_time:.1f}s)")

    return output_path