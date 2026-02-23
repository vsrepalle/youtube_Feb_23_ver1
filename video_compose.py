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
    news_type: str = "default",  # Add news_type parameter
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
    
    if audio.duration is None:
        print("[ERROR] Could not read audio duration. Check if temp/audio.mp3 is valid.")
        duration = len(english_text.split()) / 2.5 
    else:
        duration = audio.duration

    # Use speed factor from config
    speed_factor = config.AUDIO["speed_factor"]
    audio = audio.fl_time(lambda t: speed_factor * t, apply_to=['audio'])
    duration = duration / speed_factor
    audio = audio.set_duration(duration)

    print(f"[DEBUG] Audio Duration: {duration:.2f}s")

    # ───────────────────────────────────────────────
    # SLIDESHOW GENERATION
    # ───────────────────────────────────────────────
    clips = []
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

    if not clips:
        clips.append(ColorClip(size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT), color=(20, 20, 40)).set_duration(duration))

    slideshow = concatenate_videoclips(clips, method="compose")

    # ───────────────────────────────────────────────
    # HEADER (Headline Overlay) - USING CONFIG
    # ───────────────────────────────────────────────
    header_config = config.HEADER
    header_bg = (
        ColorClip(size=(config.VIDEO_WIDTH, header_config["height"]), color=header_config["background_color"])
        .set_opacity(header_config["background_opacity"])
        .set_duration(duration)
    )

    headline_clip = TextClip(
        headline.upper(),
        fontsize=header_config["fontsize"],
        color=header_config["color"],
        font=header_config["font"],
        stroke_color=header_config["stroke_color"],
        stroke_width=header_config["stroke_width"],
        size=(config.VIDEO_WIDTH - 60, None),
        method='caption',
        align='center'
    ).set_position(('center', header_config["position_y"])).set_duration(duration)

    header = CompositeVideoClip([header_bg, headline_clip]).set_position(("center", "top"))

    # ───────────────────────────────────────────────
    # SUBTITLES WITH CONFIG STYLING
    # ───────────────────────────────────────────────
    sentences = [s.strip() + '.' for s in english_text.split('.') if s.strip()]
    if not sentences:
        sentences = ["Generating content..."]
    
    # Calculate timing for each sentence
    words_per_second = len(english_text.split()) / duration
    subs = []
    
    current_time = 0
    for sentence in sentences:
        words_in_sentence = len(sentence.split())
        sentence_duration = words_in_sentence / words_per_second
        sentence_duration = max(1.5, sentence_duration)
        
        end_time = min(current_time + sentence_duration, duration)
        subs.append(((current_time, end_time), sentence))
        current_time = end_time
        
        if current_time >= duration:
            break
    
    # Get subtitle config
    sub_config = config.SUBTITLE
    
    # Create subtitle generator
    def subtitle_generator(txt):
        clip = TextClip(
            txt,
            fontsize=sub_config["fontsize"],
            color=sub_config["color"],
            stroke_color=sub_config["stroke_color"],
            stroke_width=sub_config["stroke_width"],
            font=sub_config["font"],
            size=(config.VIDEO_WIDTH - 100, None),
            method='caption',
            align='center'
        )
        
        # Add background if configured
        if sub_config["background_opacity"] > 0:
            bg = ColorClip(size=clip.size, color=sub_config["background_color"])\
                  .set_opacity(sub_config["background_opacity"])
            clip = CompositeVideoClip([bg, clip])
        
        return clip
    
    # Word-by-word highlighting
    words = english_text.split()
    word_subs = []
    word_time = 0
    word_duration = duration / len(words) if words else 0.1
    
    for word in words:
        if word_time < duration:
            end_word = min(word_time + word_duration, duration)
            word_subs.append(((word_time, end_word), word))
            word_time = end_word
    
    # Highlight generator
    def highlight_generator(txt):
        return TextClip(
            txt,
            fontsize=sub_config["fontsize"],
            color=sub_config["highlight_color"],
            stroke_color=sub_config["stroke_color"],
            stroke_width=sub_config["stroke_width"],
            font=sub_config["font"],
            size=(config.VIDEO_WIDTH - 100, None),
            method='caption',
            align='center'
        )
    
    # Position subtitles
    subtitle_y = config.VIDEO_HEIGHT - sub_config["position_y_offset"]
    subtitle_clip = SubtitlesClip(subs, subtitle_generator).set_position(('center', subtitle_y))
    highlight_clip = SubtitlesClip(word_subs, highlight_generator).set_position(('center', subtitle_y))

    # ───────────────────────────────────────────────
    # PROGRESS BAR - USING CONFIG
    # ───────────────────────────────────────────────
    bar_config = config.PROGRESS_BAR
    bar_y = config.VIDEO_HEIGHT - bar_config["position_y_offset"]
    
    progress_bg = ColorClip(size=(config.VIDEO_WIDTH, bar_config["height"]), color=bar_config["background_color"])\
                    .set_duration(duration).set_position(("left", bar_y))

    def make_progress_frame(t):
        progress_w = int(config.VIDEO_WIDTH * (t / duration))
        frame = np.zeros((bar_config["height"], config.VIDEO_WIDTH, 3), dtype=np.uint8)
        if progress_w > 0:
            frame[:, :progress_w] = bar_config["fill_color"]
        return frame

    progress_fill = VideoClip(make_progress_frame, duration=duration).set_position(("left", bar_y))

    # ───────────────────────────────────────────────
    # INITIAL HOOK - USING CONFIG
    # ───────────────────────────────────────────────
    hook_config = config.HOOK
    hook_dur = min(hook_config["duration"], duration)
    
    initial_hook = TextClip(
        hook,
        fontsize=hook_config["fontsize"],
        color=hook_config["color"],
        stroke_color=hook_config["stroke_color"],
        stroke_width=hook_config["stroke_width"],
        font=hook_config["font"],
        size=(config.VIDEO_WIDTH - 100, None),
        method='caption'
    ).set_position('center').set_duration(hook_dur)
    
    if hook_config["zoom_effect"]:
        initial_hook = initial_hook.resize(lambda t: 1 + hook_config["zoom_speed"] * t)

    # ───────────────────────────────────────────────
    # BACKGROUND MUSIC
    # ───────────────────────────────────────────────
    final_audio = audio
    
    # Try to load category-specific music
    music_path = Path(f"background_music/{news_type}_music.mp3")
    if not music_path.exists():
        music_path = Path("background_music/default_music.mp3")
    
    if music_path.exists():
        try:
            print(f"[INFO] Adding background music from {music_path}")
            bg_music = AudioFileClip(str(music_path))
            bg_music = bg_music.audio_loop(duration=duration)
            bg_music = bg_music.volumex(config.AUDIO["background_music_volume"])
            final_audio = CompositeAudioClip([audio, bg_music])
        except Exception as e:
            print(f"[WARN] Could not add background music: {e}")

    # ───────────────────────────────────────────────
    # END SCREEN - USING CONFIG
    # ───────────────────────────────────────────────
    end_config = config.END_SCREEN
    end_scr_dur = end_config["duration"]
    end_start_time = max(0, duration - end_scr_dur)

    end_bg = ColorClip(size=(config.VIDEO_WIDTH, config.VIDEO_HEIGHT), color=end_config["background_color"])\
                .set_opacity(end_config["background_opacity"]).set_duration(end_scr_dur)

    subscribe_text = TextClip(
        subscribe_hook,
        fontsize=end_config["fontsize"],
        color=end_config["color"],
        stroke_color=end_config["stroke_color"],
        stroke_width=end_config["stroke_width"],
        font=end_config["font"],
        size=(config.VIDEO_WIDTH - 120, None),
        method='caption'
    ).set_position('center').set_duration(end_scr_dur)

    end_screen = CompositeVideoClip([end_bg, subscribe_text]).set_start(end_start_time)

    # ───────────────────────────────────────────────
    # FINAL COMPOSITION
    # ───────────────────────────────────────────────
    final_video = CompositeVideoClip([
        slideshow,
        header,
        subtitle_clip,
        highlight_clip,
        progress_bg,
        progress_fill,
        initial_hook,
        end_screen
    ]).set_audio(final_audio).set_duration(duration)

    # ───────────────────────────────────────────────
    # RENDER VIDEO
    # ───────────────────────────────────────────────
    print(f"[RENDER] Writing video file to: {output_path}")
    
    final_video.write_videofile(
        output_path,
        fps=config.FPS,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        logger=None,
        preset='medium',
        bitrate='2000k'
    )

    # Close clips to free memory
    audio.close()
    if 'bg_music' in locals():
        bg_music.close()
    
    print(f"[SUCCESS] Video created: {output_path}")
    print(f"[TIMER] Total composition time: {time.time() - start_total:.2f}s")

    return output_path