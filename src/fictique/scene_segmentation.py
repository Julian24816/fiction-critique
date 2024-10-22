import asyncio
import re
from pathlib import Path
from typing import Mapping, List

import openai
from openai.types.chat import ChatCompletionMessageParam

from model.scene import Scene



async def call_llm(*messages: ChatCompletionMessageParam) -> str:
    """passes the messages to gpt-4o model and returns the resulting message content, may throw Exceptions"""
    client = openai.AsyncOpenAI()
    result = await client.chat.completions.create(model="gpt-4o", messages=messages)
    await client.close()
    return result.choices[0].message.content


scene_pattern = re.compile(
    r'^# (?P<title>.*)\n+'
    r'End: Paragraph (?P<end_paragraph>\d+) "(?P<end_excerpt>[^"]+)"\n+'
    r'Summary: (?P<summary>.*)$',
    re.MULTILINE
)

def get_scene_prompt(text: str, prev_summary: str = None, text_char_limit: int = 20000) -> List[ChatCompletionMessageParam]:
    return [
        {
            "role": "system",
            "content": "You are an assistant who helps segment stories into logical scenes and "
                       "writes one sentence summaries of the key details, e.g. who is involved, what happens and why it matters."
        },
        {
            "role": "user",
            "content": f"""Analyze the following text and identify the first scene.
A scene break should be identified by a combination of:
- A change in location, time, or key plot progression.
- A change in tone (from somber to comedic, for example).
- Introduction or conclusion of a significant interaction or emotional moment.

Return:
- The paragraph numbers where the scene ends, including a short literal excerpt of this paragraph.
- A 1 sentence summary of the scene's key events and shifts.

Ensure the result matches this regex pattern in the next three rows, especially the " marks, don't enclose it in backticks, and don't include anything else in your answer. Be careful not to include " in the excerpts.
# (?P<scene_title>.*)
End: Paragraph (?P<end_paragraph>\\d+) "(?P<end_excerpt>[^"]+)"
Summary: (?P<summary>.*)

{f"Previous Scene Summary:\n{prev_summary}\n" if prev_summary else ""}Text:
{text[:text_char_limit]}
"""
        }
    ]

def index_containing(lst: List[str], excerpt: str) -> int:
    for i, s in enumerate(lst):
        if excerpt in s:
            return i
    return -1

def parse_scene(answer: str, full_text: str, verbose: bool = False) -> Scene:
    match = scene_pattern.match(answer)
    if match is None:
        raise ValueError(f"couldn't find match in {answer}")

    paragraphs = full_text.split("\n\n")
    end_paragraph = int(match.group("end_paragraph"))
    detected_end_paragraph = index_containing(paragraphs, match.group("end_excerpt").strip("."))
    if detected_end_paragraph == -1:
        if verbose: print("couldn't find excerpt, going with llm designated end paragraph:", end_paragraph)
    elif end_paragraph != detected_end_paragraph:
        end_paragraph = detected_end_paragraph
        if verbose: print("detected end paragraph differed from llm designated one, using detected:", end_paragraph)
    if end_paragraph >= len(paragraphs):
        end_paragraph = len(paragraphs) - 1
        if verbose: print("limiting end paragraph to last paragraph")

    return Scene(
        title=match.group("title"),
        summary=match.group("summary"),
        text="\n\n".join(paragraphs[:end_paragraph])
    )

async def prompt_and_parse_scene(messages, remaining_text) -> Scene:
    result = await call_llm(*messages)
    return parse_scene(result, remaining_text)

def prompt_next_scene(remaining_text: str, async_tries: int, prev_summary: str = None) -> Scene | None:
    try:
        messages = get_scene_prompt(remaining_text, prev_summary)
        if async_tries >= 2:
            # call llm asynchronously and return result with median length
            async def task():
                tasks = [prompt_and_parse_scene(messages, remaining_text) for _ in range(async_tries)]
                tasks = await asyncio.gather(*tasks, return_exceptions=True)
                scenes = [t for t in tasks if not isinstance(t, Exception)]
                exceptions = [t for t in tasks if isinstance(t, Exception)]
                if len(scenes) == 0: raise exceptions[0]
                if len(scenes) == 1: return scenes[0]
                scenes.sort(key=lambda s: s.text.count("\n\n"))
                return scenes[len(scenes) // 2]
            return asyncio.run(task())
        else:
            return asyncio.run(prompt_and_parse_scene(messages, remaining_text))
    except Exception as e:
        print("Exception while prompting next scene:", e)
        return None


# Function to segment the text into scenes
def segment_text(file_path: Path, start_with_first_h2: bool = True, async_tries: int = 3, verbosity: int = 1) -> List[Scene]:
    """uses openai to segment the text in the provided file into scenes. verbosity: 0..2"""
    with file_path.open(encoding="utf-8") as file:
        text = file.read().lstrip("\n")
        if start_with_first_h2:
            text = text[text.find("##"):]

    scenes: List[Scene] = []
    scene = prompt_next_scene(text, async_tries)

    while scene is not None:
        if verbosity > 0:
            print("detected scene:", scene.title)
            if verbosity > 1: print(scene, "\n")
        scenes.append(scene)
        text = text[len(scene.text):].lstrip("\n")
        if text == "":
            break
        scene = prompt_next_scene(text, async_tries, scene.summary)

    return scenes