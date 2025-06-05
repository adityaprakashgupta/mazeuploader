from moviepy import *
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import emoji

video_width = 1080
video_height = 1920
image_width = 1080
image_height = 1080
target_resolution = (video_width, video_height)
image_size = (image_width, image_height)


def is_emoji(char):
    return char in emoji.EMOJI_DATA


def get_word_width(word, text_font, fontsize):
    width = 0
    for char in word:
        if is_emoji(char):
            width += fontsize
        else:
            bbox = text_font.getbbox(char)
            width += bbox[2] - bbox[0]
    return width


def wrap_text_by_words(text, text_font, max_width, fontsize):
    words = text.split(" ")
    space_width = text_font.getbbox(" ")[2] - text_font.getbbox(" ")[0]

    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width = get_word_width(word, text_font, fontsize)
        space = space_width if current_line else 0

        if current_width + word_width + space <= max_width:
            current_line.append(word)
            current_width += word_width + space
        else:
            if current_line:
                lines.append(current_line)
            if word_width > max_width:
                # fallback to char-based split for long words
                split = list(word)
                for c in split:
                    if (
                        not lines
                        or get_word_width("".join(lines[-1]) + c, text_font, fontsize)
                        > max_width
                    ):
                        lines.append([c])
                    else:
                        lines[-1].append(c)
                current_line = []
                current_width = 0
            else:
                current_line = [word]
                current_width = word_width

    if current_line:
        lines.append(current_line)
    return lines


class VideoEditor:
    def __init__(self, mazes, output_path, color_scheme=None, font_scheme=None):
        self.mazes = mazes
        self.output_path = output_path
        self.font_scheme = font_scheme or {
            "text_font": "video_editor/fonts/Benton Modern Text Bold.otf",
            "cta_font": "video_editor/fonts/Benton Modern D SemiBold Italic.otf",
            "timer_font": "video_editor/fonts/BebasNeue-Regular.ttf",
        }
        self.font_scheme["emoji_font"] = "video_editor/fonts/NotoColorEmoji.ttf"
        self.clips = (
            self.create_sequence(**color_scheme)
            if color_scheme
            else self.create_sequence()
        )

    def create_sequence(
        self, bg_color=(0, 0, 0), text_color=(255, 255, 255), strap_color=(255, 255, 0)
    ):
        clips = []
        paste_x = (video_width - image_width) // 2
        paste_y = (video_height - image_height) // 2
        paste_coords = (paste_x, paste_y)

        for maze in self.mazes:
            timer_clip = self.generate_timer_clips(
                maze["duration"],
                text=maze["timer_text"],
                display_timer=maze["timer"],
                text_color=text_color,
            )
            timer_clip_height = timer_clip.size[1]
            timer_clip = timer_clip.with_position(
                ("center", 110 + (310 - timer_clip_height) // 2)
            )
            background = Image.new("RGB", target_resolution, color=bg_color)
            top_text = self.make_text(
                text=maze["label"],
                color=bg_color,
                size=(video_width, 110),
                strap_color=strap_color,
            )
            lines = wrap_text_by_words(
                maze["cta"],
                ImageFont.truetype(
                    self.font_scheme["cta_font"][0], self.font_scheme["cta_font"][1]
                ),
                video_width,
                self.font_scheme["cta_font"][1],
            )
            lines = "\n".join([" ".join(line).strip() for line in lines])
            cta_image = TextClip(
                self.font_scheme["cta_font"][0],
                text=lines,
                font_size=self.font_scheme["cta_font"][1],
                color=text_color,
                text_align="center",
            ).with_duration(maze["duration"])
            cta_clip_height = cta_image.size[1]
            cta_image = cta_image.with_position(
                ("center", (1500 + (420 - cta_clip_height) // 2) - 50)
            )
            background.paste(maze["image"], paste_coords)
            background.paste(top_text, (0, 0), top_text.convert("RGBA"))
            img_array = np.array(background)
            img_clip = ImageClip(img_array, duration=maze["duration"])
            combined_clip = CompositeVideoClip([img_clip, timer_clip, cta_image])
            clips.append(combined_clip)

        return clips

    def create_video(self, preview=False):
        video_clip = concatenate_videoclips(self.clips)
        if preview:
            video_clip.show(2)
            video_clip.show(9)
            video_clip.show(59)
        else:
            video_clip.write_videofile(self.output_path, fps=1)

    def generate_timer_clips(
        self, duration, text="", display_timer=True, text_color="white"
    ):
        font_size = self.font_scheme["timer_font"][1]
        timer_clips = []
        if not display_timer:
            timer_clips.append(
                TextClip(
                    text=text,
                    font_size=font_size,
                    color=text_color,
                    font=self.font_scheme["timer_font"][0],
                    text_align="center",
                ).with_duration(duration)
            )
            return concatenate_videoclips(timer_clips)
        else:
            audio_clip = (
                AudioFileClip("video_editor/audios/tick-tock.mp3")
                .with_duration(20)
                .with_effects([afx.AudioLoop(duration=duration)])
            )
            for i in range(duration, 0, -1):
                minutes = int(i // 60)
                seconds = int(i % 60)
                time_str = f"{minutes:02}:{seconds:02}"
                time_str = f"{text} {time_str}" if text else time_str
                timer_text = TextClip(
                    text=time_str,
                    font_size=font_size,
                    color=text_color,
                    font=self.font_scheme["timer_font"][0],
                    text_align="center",
                )
                timer_text = timer_text.with_duration(1)
                timer_clips.append(timer_text)
            return concatenate_videoclips(timer_clips).with_audio(audio_clip)

    def make_text(
        self,
        text,
        color="white",
        size=(video_width, 100),
        strap_color=(0, 0, 0, 0),
    ):
        font_size = self.font_scheme["text_font"][1]
        img = Image.new("RGBA", size, strap_color)
        draw = ImageDraw.Draw(img)
        text_font = ImageFont.truetype(self.font_scheme["text_font"][0], font_size)
        bbox = draw.textbbox((0, 0), text, font=text_font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) / 2
        y = (size[1] - text_height) / 2 - bbox[
            1
        ]  # Center vertically, adjust for baseline
        draw.text((x, y), text, font=text_font, fill=color)
        return img

    def render_emoji(self, char, target_size):
        # Render emoji at large size
        emoji_font = ImageFont.truetype(self.font_scheme["emoji_font"], 109)
        bbox = emoji_font.getbbox(char)
        img = Image.new(
            "RGBA", (int(bbox[2] - bbox[0]), int(bbox[3] - bbox[1])), (0, 0, 0, 0)
        )
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, font=emoji_font, embedded_color=True)

        # Resize to match target size
        emoji_resized = img.resize((target_size, target_size))
        return emoji_resized
