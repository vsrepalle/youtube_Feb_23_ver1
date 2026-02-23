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
    
    if audio.duration is None:
        print("[ERROR] Could not read audio duration. Check if temp/audio.mp3 is valid.")
        duration = len(english_text.split()) / 2.5 
    else:
        duration = audio.duration

    speed_factor = 1.2
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
    # FIXED: ENGLISH SUBTITLES WITH WORD HIGHLIGHTING
    # ───────────────────────────────────────────────
    
    # Split text into sentences
    sentences = [s.strip() + '.' for s in english_text.split('.') if s.strip()]
    if not sentences:
        sentences = ["Generating content..."]
    
    # Calculate timing for each sentence
    words_per_second = len(english_text.split()) / duration
    subs = []
    
    current_time = 0
    for sentence in sentences:
        # Calculate duration for this sentence based on word count
        words_in_sentence = len(sentence.split())
        sentence_duration = words_in_sentence / words_per_second
        
        # Ensure minimum duration
        sentence_duration = max(1.5, sentence_duration)
        
        end_time = min(current_time + sentence_duration, duration)
        subs.append(((current_time, end_time), sentence))
        current_time = end_time
        
        if current_time >= duration:
            break
    
    # Create subtitle generator with better styling
    def subtitle_generator(txt):
        # Create main subtitle text
        return TextClip(
            txt,
            fontsize=55,
            color='white',  # Default white
            stroke_color='black',
            stroke_width=3,
            font='Arial-Bold',
            size=(config.VIDEO_WIDTH - 100, None),
            method='caption',
            align='center'
        )
    
    # Create subtitle clip
    subtitle_clip = SubtitlesClip(subs, subtitle_generator)
    
    # Create a yellow highlight overlay that fades in/out with each word
    # For simplicity, we'll create a second subtitle clip with yellow color
    # that appears at the same times
    
    # Split into smaller chunks for word-by-word highlighting
    words = english_text.split()
    word_subs = []
    word_time = 0
    word_duration = duration / len(words) if words else 0.1
    
    for word in words:
        if word_time < duration:
            end_word = min(word_time + word_duration, duration)
            word_subs.append(((word_time, end_word), word))
            word_time = end_word
    
    # Generator for highlighted words (yellow)
    def highlight_generator(txt):
        return TextClip(
            txt,
            fontsize=55,
            color='yellow',  # Yellow for highlighting
            stroke_color='black',
            stroke_width=3,
            font='Arial-Bold',
            size=(config.VIDEO_WIDTH - 100, None),
            method='caption',
            align='center'
        )
    
    # Create highlighted word clip
    highlight_clip = SubtitlesClip(word_subs, highlight_generator)
    
    # Position both subtitle clips
    subtitle_y = config.VIDEO_HEIGHT - 250
    subtitle_clip = subtitle_clip.set_position(('center', subtitle_y))
    highlight_clip = highlight_clip.set_position(('center', subtitle_y))
    
    # Combine them - the yellow words will appear on top of white text
    # But since they're positioned exactly the same, we need to handle this differently
    
    # Better approach: Create a single clip with dynamic coloring
    # But for now, we'll create a composite that shows yellow highlights
    
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
    # INITIAL HOOK (Zoom effect)
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
    # FIXED: BACKGROUND MUSIC
    # ───────────────────────────────────────────────
    final_audio = audio  # Start with voice audio
    
    try:
        # Check if background music file exists
        music_path = "background_music.mp3"
        if Path(music_path).exists():
            print("[INFO] Adding background music...")
            bg_music = AudioFileClip(music_path)
            
            # Loop the music to match video duration
            n_loops = int(duration / bg_music.duration) + 1
            bg_music = bg_music.audio_loop(duration=duration)
            
            # Reduce volume (0.1 = 10% volume)
            bg_music = bg_music.volumex(0.08)
            
            # Composite audio (voice + music)
            final_audio = CompositeAudioClip([audio, bg_music])
            print("[INFO] Background music added successfully")
        else:
            print(f"[WARN] Background music file not found at: {music_path}")
            print("[INFO] Continuing without background music")
    except Exception as e:
        print(f"[WARN] Could not add background music: {e}")
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
    # FINAL COMPOSITION
    # ───────────────────────────────────────────────
    
    # For word highlighting, we need a more sophisticated approach
    # Simple approach: Just use the highlight clip alone (yellow words only)
    # This ensures spoken words are highlighted in yellow
    
    # Or use both but position them differently? Let's use just yellow for now
    # to clearly show highlighting
    
    print("[INFO] Creating video with yellow word highlighting...")
    
    # Option 1: Yellow only (spoken words in yellow)
    final_video = CompositeVideoClip([
        slideshow,
        header,
        highlight_clip,  # Only yellow words (this will show spoken words in yellow)
        progress_bg,
        progress_fill,
        initial_hook,
        end_screen
    ]).set_audio(final_audio).set_duration(duration)
    
    # Option 2: If you want both white text and yellow highlights, use this:
    # final_video = CompositeVideoClip([
    #     slideshow,
    #     header,
    #     subtitle_clip,   # White text background
    #     highlight_clip,  # Yellow highlights on top
    #     progress_bg,
    #     progress_fill,
    #     initial_hook,
    #     end_screen
    # ]).set_audio(final_audio).set_duration(duration)

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