import os
from content_ai.generator import LLMProvider
from pydantic import BaseModel


class BrandContent(BaseModel):
    name: str
    username: str
    logo_prompt: str
    banner_prompt: str
    description: str


class MultiBrandContent(BaseModel):
    contents: list[BrandContent]


def generate_full_youtube_prompt(levels: list[str], theme: str) -> str:
    level_map = {"B": "Beginner", "M": "Medium", "H": "Hard"}
    full_levels = [level_map.get(level.upper(), level) for level in levels]
    level_text = ", ".join(full_levels) if full_levels else "varied levels"

    theme = theme.lower()
    tone = "mysterious and challenging" if theme == "dark" else "bright and energetic"
    # visual_style = (
    #     "dark, shadowy tones and bold highlights"
    #     if theme == "dark"
    #     else "light, clean colors with vibrant gradients"
    # )

    return f"""You are a branding expert helping design a YouTube channel for puzzle and logic-based content.

Based on the following metadata:
- Puzzle difficulty levels: {level_text}
- Channel theme: {theme} (tone: {tone})

Generate the following:

1. A **catchy YouTube channel name** that reflects puzzles, mazes, and mental challenges. Not common names give some unique names because common names are already taken. can also include meaningful numbers at end to make it unique.
2. A **YouTube username/handle** (in @format), short, brandable, and derived from the name.
3. A **logo prompt** (text-only) to be used in an AI image generator. The prompt should describe a logo matching the name, theme, and tone — suitable for a circular YouTube profile picture.
4. A **banner prompt** (text-only) to be used in an AI image generator. The prompt should describe a banner image suitable for YouTube (2560×1440 px, safe zone: 1546×423 px) that aligns with the channel’s theme and difficulty levels. Include visual metaphors like mazes, grids, glowing paths, brain icons, etc. It should be very detailed and avoid text on banners just want good visuals.
5. A **SEO-optimized channel description** (120–160 words) that clearly states the channel’s focus, target audience (puzzle lovers, brain game fans), includes the levels ({level_text}), encourages subscribing, and uses tone: {tone}. It should contains emojis and must be multi line with about 100-150 words. Use a friendly, engaging tone that invites viewers to join the puzzle-solving journey.

Output the response in clear labeled sections, **no extra commentary**, no repeated instructions.
generate the 15 ideas for each section, and make sure they are unique and creative.
"""


def generate(levels=["B", "M", "H"], theme="light") -> MultiBrandContent:
    client = LLMProvider(
        "openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE")
    )
    prompt = generate_full_youtube_prompt(levels, theme)
    model = os.getenv("OPENAI_MODEL_NAME")
    contents = prompt

    resp = client.generate_content(
        model=model, contents=contents, response_schema=MultiBrandContent
    )

    return resp


if __name__ == "__main__":
    datas = generate(["H"], "dark")
    for data in datas.contents:
        print("Name:", data.name)
        print("Username:", data.username)
        print("Logo Prompt:", data.logo_prompt)
        print("Banner Prompt:", data.banner_prompt)
        print("Description:", data.description)
        print("-" * 40)
