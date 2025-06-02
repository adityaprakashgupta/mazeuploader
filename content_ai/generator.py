import os
import random
from google import genai
from openai import OpenAI
from google.genai import types
from pydantic import BaseModel


class VideoContent(BaseModel):
    title: str
    description: str
    tags: list[str]


class LLMProvider:
    def __init__(self, provider: str, api_key: str, **kwargs):
        if provider == "google":
            self.client = genai.Client(api_key=api_key, **kwargs)
        if provider == "openai":
            self.client = OpenAI(api_key=api_key, **kwargs)

    def generate_content(self, model: str, contents: str, response_schema: BaseModel):
        if isinstance(self.client, genai.Client):
            return self.generate_content_google(model, contents, response_schema)
        elif isinstance(self.client, OpenAI):
            return self.generate_content_openai(model, contents, response_schema)
        else:
            raise ValueError("Unsupported client type")

    def generate_content_google(
        self, model: str, contents: str, response_schema: BaseModel
    ):
        generate_content_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0),
            response_mime_type="application/json",
            response_schema=response_schema,
        )
        resp = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        return resp.parsed

    def generate_content_openai(
        self, model: str, prompt: str, response_schema: BaseModel
    ):
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=response_schema,
            seed=random.randint(1, 1000000),
        )
        return response.choices[0].message.parsed


def generate_maze_prompt(levels: list, duration: int) -> str:
    """
    Generate a dynamic prompt to feed into a title+description generator for a maze video.

    Parameters:
    - levels: List of strings like ["B", "M", "H"] representing Basic, Medium, Hard
    - duration: Total video duration in seconds

    Returns:
    - A formatted string prompt ready to use with GPT for SEO content generation
    """
    level_map = {"B": "easy", "M": "medium", "H": "hard"}

    # Convert levels to readable strings
    readable_levels = [level_map.get(level, "unknown") for level in levels]
    num_levels = len(readable_levels)
    level_str = ", ".join(readable_levels)

    prompt = f"""
Generate a highly engaging, SEO-optimized YouTube title, description and tags for a Shorts video that features maze puzzles.
The video includes {num_levels} level{"s" if num_levels > 1 else ""} (types: {level_str}) and has a total duration of {duration} seconds.
The tone should be playful, curious, and challenge-oriented.
The title must grab attention in under 60 characters and contain keywords like 'maze', 'puzzle', 'brain game', or 'can you solve'.
The description should include SEO keywords naturally (maze puzzle, brain teaser, logic game, short puzzle video, quick challenge, etc.),
a brief summary of what viewers can expect, a call-to-action to subscribe, and hashtags relevant for Shorts and puzzles.
Make sure the title and description are tailored to boost click-through rate and viewer retention also add some emoji and for good feel.
"""
    return prompt.strip()


def generate(levels=["B", "M", "H"], duration=60, provider="google") -> VideoContent:
    if provider == "google":
        kwargs = dict(api_key=os.getenv("GOOGLE_API_KEY"))
        model = os.getenv("GOOGLE_MODEL_NAME")
    elif provider == "openai":
        kwargs = dict(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )
        model = os.getenv("OPENAI_MODEL_NAME")
    else:
        raise ValueError("Unsupported provider. Use 'google' or 'openai'.")
    client = LLMProvider(provider, **kwargs)
    prompt = generate_maze_prompt(levels, duration)
    contents = prompt
    response_schema = VideoContent
    resp = client.generate_content(
        model=model, contents=contents, response_schema=response_schema
    )
    return resp


if __name__ == "__main__":
    data = generate(provider="openai")
    print("Title:", data.title)
    print("Description:", data.description)
    print("Tags:", data.tags)
