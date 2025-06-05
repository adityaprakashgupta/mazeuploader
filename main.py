from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
from video_uploader.uploader import YouTubeUploader
from maze_generator import Maze
import os
from video_editor.editor import VideoEditor
from content_ai.generator import generate
import random
from content_ai.generator import VideoContent
import json
from collections import Counter

done_file = "done.txt"

def mark_done(channel_id: str, lock):
    with lock:
        with open(done_file, "a") as f:
            f.write(f"{channel_id}\n")


def load_done_counts():
    if os.path.exists(done_file):
        with open(done_file) as f:
            return Counter(line.strip() for line in f)
    return Counter()


def get_maze(level: str, color_scheme=None):
    match level:
        case "B":
            MAZE_HEIGHT = MAZE_WIDTH = 12
        case "M":
            MAZE_HEIGHT = MAZE_WIDTH = 20
        case "H":
            MAZE_HEIGHT = MAZE_WIDTH = 30
        case _:
            raise Exception(f"Unknown maze level: {level}")
    UNIT_SIZE = 500 // MAZE_WIDTH
    WALL_THICKNESS = 300 // MAZE_WIDTH
    SOLUTION_WIDTH = 200 // MAZE_WIDTH
    SOLUTION_WIDTH = min(SOLUTION_WIDTH, UNIT_SIZE)  # Ensure solution fits
    maze_obj = Maze(MAZE_HEIGHT, MAZE_WIDTH, color_scheme)
    maze_obj.generate()
    maze_obj.solve()

    maze_img = maze_obj.save_image(
        None,
        unit_size=UNIT_SIZE,
        wall_thickness=WALL_THICKNESS,
        show_solution=False,
        solution_width=SOLUTION_WIDTH,  # Pass solution width even if not shown, for consistency
    )

    solution_img = maze_obj.save_image(
        None,
        unit_size=UNIT_SIZE,
        wall_thickness=WALL_THICKNESS,
        show_solution=True,
        solution_width=SOLUTION_WIDTH,  # Pass solution width even if not shown, for consistency
    )

    return maze_img, solution_img


def get_duration(
    level: str,
    total_duration: int = 60,
    solution_duration: int = 2,
    total_levels: int = 3,
    high_only: bool = False,
):
    if total_levels <= 0:
        raise ValueError("Total levels must be greater than 0")
    if total_duration <= 0:
        raise ValueError("Total duration must be greater than 0")
    if solution_duration < 0:
        raise ValueError("Solution duration cannot be negative")
    total_duration = total_duration - (solution_duration * total_levels)
    if total_duration <= 0:
        raise ValueError(
            "Total duration must be greater than solution duration times total levels"
        )
    # divide the remaining time in ratio of 1:2:3 for easy, medium, and hard levels
    if level not in ["B", "M", "H"]:
        raise ValueError("Level must be one of 'B', 'M', or 'H'")

    if high_only and level == "H":
        return total_duration // total_levels
    if level == "B":
        return total_duration // 6
    elif level == "M":
        return total_duration // 3
    elif level == "H":
        return total_duration // 2

    return None


def get_ctas(level: str, total_levels: int = 3):
    easy_ctas = [
        "Warm-up time! Can you solve this one fast?",
        "Start strong! Get this easy one right.",
        "Ready? Let’s see how sharp you are!",
        "Level 1: Just the beginning...",
        "If this one's tricky, you're in for a ride!",
        "This is just to wake up your brain",
    ]
    medium_ctas = [
        "Not so easy now, huh?",
        "Level 2: Let’s turn up the heat",
        "Think you're doing great? Prove it here.",
        "Time to put those brain cells to work!",
        "Let’s see if you’re still on a winning streak!",
        "Getting serious now. Can you handle it?",
        "Think that was tough? Wait for the next one!",
    ]
    hard_ctas = [
        "Missed one? Rewind and try again!",
        "Think you can solve it faster? Watch again!",
        "Level up your brain – can you beat it in one go?",
        "Tag a friend who loves puzzles!",
        "1 try or more? Let us know below!",
        "More mazes coming soon – follow to stay sharp!",
        "Next challenge drops tomorrow – don’t miss it!",
        "Your brain’s just getting started – more ahead!",
        "Puzzle Over? Prove it.\nFollow | Like | Comment",
    ]
    if total_levels > 1:
        easy_ctas += []
        medium_ctas += []
        hard_ctas += [
            "Did you solve it? Let’s see if you can keep up!",
            "If you got this far, you’re a maze master!",
            "Final level! Can you conquer it?",
            "Last chance to prove your maze-solving skills!",
            "You made it to the end! How many did you solve?",
            "Comment ‘fire’ if you solved all 3!",
            "Which was hardest? 1st, 2nd, or 3rd?",
            "Which maze got you? Drop the level in comments!",
        ]
    match level:
        case "B":
            return random.choice(easy_ctas)
        case "M":
            return random.choice(medium_ctas)
        case "H":
            return random.choice(hard_ctas)
        case _:
            raise Exception(f"Unknown maze level: {level}")


def get_timer_text(
    level: str,
    solution_position: int = 0,
    total_levels: int = 3,
    high_only: bool = False,
    current_level: int = 1,
):
    maze_timer_text = ""
    solution_timer_text = ""
    if solution_position == 0 and total_levels > 1:
        if level in ["B", "M"]:
            maze_timer_text = "Solution in:"
            solution_timer_text = "Next level in:"
        if level == "H":
            maze_timer_text = "Solution in:"
            solution_timer_text = "Thank you for watching!"
            if high_only and current_level < total_levels:
                solution_timer_text = "Next level in:"
    elif solution_position == 1:
        if level in ["B", "M", "H"]:
            maze_timer_text = "Next level in:"
            solution_timer_text = "Thank you for watching!"
        if current_level == total_levels:
            maze_timer_text = "Solutions in:"
    elif solution_position == -1:
        if level in ["B", "M"]:
            maze_timer_text = "Next level in:"
            solution_timer_text = ""
        if level == "H":
            if high_only and current_level < total_levels:
                maze_timer_text = "Next level in:"
                solution_timer_text = ""
            if current_level == total_levels:
                maze_timer_text = "Thank you for watching!\nTime left:"
                solution_timer_text = ""

    return maze_timer_text, solution_timer_text


def main(
    levels=None,
    total_duration=None,
    solution_duration=None,
    solution_position=0,
    creds=None,
    color_scheme=None,
    font_scheme=None,
    upload=True,
):
    levels = levels or ["B", "M", "H"]  # Default levels if not provided
    total_duration = total_duration or 60  # Default total duration in seconds
    solution_duration = solution_duration
    solution_position = (
        solution_position if solution_position in [-1, 0, 1] else 0
    )  # Default to mid if invalid
    cta2 = get_ctas("H", len(levels))

    high_only = False
    if list(set(levels)) == ["H"]:
        high_only = True

    clips = []
    solution_clips = []
    for idx, level in enumerate(levels):
        timer = idx < len(levels) - 1 and solution_position == 0
        maze_timer_text, solution_timer_text = get_timer_text(
            level, solution_position, len(levels), high_only, idx + 1
        )
        cta = get_ctas(level, len(levels))
        if len(levels) == 1:
            label_text = "Solve this maze!"
            solution_label_text = "Solution"
        else:
            label_text = f"Level {idx + 1} of {len(levels)}"
            solution_label_text = f"Solution of level {idx + 1}"

        maze_img, solution_img = get_maze(level, color_scheme=color_scheme["maze"])
        maze_img = maze_img.resize((1080, 1080))
        solution_img = solution_img.resize((1080, 1080))
        clips.append(
            {
                "image": maze_img,
                "label": label_text,
                "duration": get_duration(
                    level, total_duration, solution_duration, len(levels), high_only
                ),
                "timer": True,
                "timer_text": maze_timer_text,
                "cta": cta,
            }
        )
        if solution_position == 0:
            clips.append(
                {
                    "image": solution_img,
                    "label": solution_label_text,
                    "duration": solution_duration,
                    "timer": timer,
                    "timer_text": solution_timer_text,
                    "cta": cta,
                }
            )
        if solution_position == 1:
            solution_clips.append(
                {
                    "image": solution_img,
                    "label": solution_label_text,
                    "duration": solution_duration,
                    "timer": False,
                    "timer_text": solution_timer_text,
                    "cta": cta2,
                }
            )
    clips += solution_clips
    os.makedirs("output", exist_ok=True)

    random_path = os.path.join("output", f"maze_{random.randint(10000, 99999)}.mp4")

    video_editor = VideoEditor(
        clips, random_path, color_scheme=color_scheme["video"], font_scheme=font_scheme
    )
    video_editor.create_video(preview=False)

    if upload:

        try:
            meta = generate(levels, total_duration, "openai")
        except Exception:
            try:
                meta = generate(levels, total_duration, "google")
            except Exception:
                meta = VideoContent(
                    title="Maze Challenge",
                    description="Can you solve this maze? Watch the video and try to beat the time!",
                    tags=["maze", "puzzle", "shorts", "brain game", "can you solve"],
                )

        # Upload the video to YouTube
        uploader = YouTubeUploader(creds)
        response = uploader.upload_video(
            random_path,
            title=meta.title,
            description=meta.description,
            category_id=20,
            privacy_status="public",
            made_for_kids=False,
            tags=meta.tags
            or [
                "maze",
                "puzzle",
                "shorts",
                "brain game",
                "can you solve",
                "short puzzle video",
                "quick challenge",
            ],
        )
        print(f"Video uploaded successfully: https://youtube.com/shorts/{response['id']}")
    os.remove(random_path)


if __name__ == "__main__":
    from database.client import YouTubeDB
    import os

    runtime = os.getenv("RUNTIME", "local").lower()
    if runtime == "local":
        print("Running in local mode. Loading environment variables from .env file.")
        from dotenv import load_dotenv
        load_dotenv(".env")

    mongo_uri = os.getenv("MONGO_URI")
    db = YouTubeDB(mongo_uri)

    test_mode = os.environ.get("TEST_MODE", "false").lower() == "true"

    upload = os.environ.get("UPLOAD", "true").lower() == "true"

    multiplier = os.getenv("MULTIPLIER")

    workers = os.getenv("WORKERS")

    if workers:
        try:
            workers = int(workers)
        except ValueError:
            print(f"Invalid WORKERS value: {workers}. Defaulting to 4.")
            workers = None

    if workers is None:
        workers = max(1, os.cpu_count())

    if multiplier:
        try:
            multiplier = int(multiplier)
        except ValueError:
            print(f"Invalid MULTIPLIER value: {multiplier}. Defaulting to 1.")
            multiplier = None

    if multiplier is None:
        multiplier = 1 if test_mode else 2

    print(f"Running in test mode: {test_mode}")

    clannels = os.getenv("CHANNELS")

    if clannels:
        try:
            channels = json.loads(clannels)
        except json.JSONDecodeError:
            print(f"Invalid CHANNELS JSON: {clannels}. Fetching from database instead.")
            channels = None

    if not clannels:
        print("Fetching channels from database...")
        channels = db.get_all_channels(test=test_mode)

    channels = [channel["channel_id"] for channel in channels * multiplier]

    required_counts = Counter(channels)
    completed_counts = load_done_counts()

    # Determine how many times each is still pending
    remaining = []
    for ch in required_counts:
        remaining_count = required_counts[ch] - completed_counts[ch]
        remaining.extend([ch] * remaining_count)

    def create_video_instance(channel_id, lock):
        global db, upload
        (
            creds,
            font_scheme,
            color_scheme,
            levels,
            total_duration,
            solution_duration,
            solution_position,
        ) = db.get_channel_data(channel_id)
        print(
            f"Creating video for channel {channel_id} with levels {levels}, total duration {total_duration}, solution duration {solution_duration}, solution position {solution_position}"
        )
        try:
            main(
                levels=levels,
                total_duration=total_duration,
                solution_duration=solution_duration,
                solution_position=solution_position,
                creds=creds,
                color_scheme=color_scheme,
                font_scheme=font_scheme,
                upload=upload,
            )
            mark_done(channel_id, lock)
        except Exception as e:
            print(f"❌ Error creating video for channel {channel_id}: {e}")
        print(f"✅ Video created successfully for channel {channel_id}")

    manager = multiprocessing.Manager()
    lock = manager.Lock()

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(create_video_instance, channel, lock) for channel in remaining
        ]
        for future in tqdm(
            as_completed(futures), total=len(futures), desc="Processing videos"
        ):
            try:
                future.result()
            except Exception as e:
                print(f"Error in thread: {e}")

    if runtime == "gcp":
        from runtime import delete_instance
        print("Deleting instance...")
        delete_instance()
