import marimo

__generated_with = "0.19.4"
app = marimo.App(width="columns")


@app.cell(column=0)
def _():
    import marimo as mo
    from IPython.display import Markdown, display
    return Markdown, mo


@app.cell
def _():
    from pathlib import Path
    from dotenv import load_dotenv

    try:
        start = Path(__file__).resolve()
    except NameError:
        start = Path.cwd()

    supporting_files = next(p / "00-supporting-files" for p in start.parents if (p / "00-supporting-files").exists())
    return Path, start, supporting_files


@app.cell
def _(start):
    project_parent = next(p for p in (start.resolve(), *start.resolve().parents) if (p / "00-supporting-files").exists()).parent
    project_parent
    return (project_parent,)


@app.cell
def _(project_parent):
    video_dir = project_parent / "large-files"
    video_dir
    return (video_dir,)


@app.cell
def _():
    # files = [file.name for file in Path(video_dir).iterdir()]
    # files
    return


@app.cell
def _():
    # p = video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0-av1_15mb_audio.webm"
    # # p = video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.mkv"
    # mo.Html(f"""
    # <video controls style="max-width: 100%; height: auto;">
    #   <source src="{p}" type="video/mp4">
    # </video>
    # """)
    return


@app.cell
def _(supporting_files):
    data_dir = supporting_files / "data"
    return (data_dir,)


@app.cell
def _(supporting_files):
    compressed_frame = supporting_files / "data" / "compressed_frame.png"
    compressed_frame
    return (compressed_frame,)


@app.cell
def _(supporting_files):
    source_frame = supporting_files / "data" / "source_frame.png"
    source_frame
    return (source_frame,)


@app.cell
def _(compressed_frame, p, shlex, subprocess):
    # import subprocess, shlex

    cmd = f'ffmpeg -v error -ss 5.2 -i {'"' + str(p) + '"'} -compressed_frames:v 1 -update 1 {compressed_frame}'
    output = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    print("returncode:", output.returncode)
    print("stderr:", output.stderr.strip())
    return (output,)


@app.cell
def _(output):
    output
    return


@app.cell
def _():
    # # Notebook cell: OpenCV + AV1 diagnostics on NixOS (software vs VAAPI, and which FFmpeg libs are loaded)

    # import os
    # import sys
    # import subprocess

    # VIDEO = str(video_dir / "better-video-qualityDoug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.15mb.webm")

    # def sh(*cmd: str) -> int:
    #     print("\n$", " ".join(cmd))
    #     p = subprocess.run(cmd, text=True, capture_output=True)
    #     if p.stdout:
    #         print(p.stdout.rstrip())
    #     if p.stderr:
    #         print(p.stderr.rstrip())
    #     return p.returncode

    # def print_section(title: str) -> None:
    #     print("\n" + "=" * 80)
    #     print(title)
    #     print("=" * 80)

    # print_section("1) System checks (ffprobe/ffmpeg/VAAPI)")
    # sh("which", "ffmpeg")
    # sh("which", "ffprobe")
    # sh("ffprobe", "-hide_banner", "-select_streams", "v:0", "-show_entries", "stream=codec_name,pix_fmt,width,height,avg_compressed_frame_rate", "-of", "default=nw=1", VIDEO)

    # # ffmpeg software decode test (first compressed_frame)
    # sh("ffmpeg", "-hide_banner", "-v", "error", "-i", VIDEO, "-compressed_frames:v", "1", "-f", "null", "-")

    # # VAAPI capability check via vainfo (uses nix shell if vainfo not installed)
    # if sh("bash", "-lc", "command -v vainfo >/dev/null") != 0:
    #     sh("nix", "shell", "nixpkgs#libva-utils", "-c", "vainfo")
    # else:
    #     sh("vainfo")

    # # ffmpeg VAAPI decode test (first compressed_frame)
    # sh("bash", "-lc", f"ls -l /dev/dri/renderD* || true")
    # sh("ffmpeg", "-hide_banner", "-v", "error",
    #    "-vaapi_device", "/dev/dri/renderD128",
    #    "-hwaccel", "vaapi", "-hwaccel_output_format", "vaapi",
    #    "-i", VIDEO, "-compressed_frames:v", "1", "-f", "null", "-")

    # print_section("2) OpenCV build + linked FFmpeg libraries")
    # import cv2

    # print("cv2.__version__:", cv2.__version__)
    # print("cv2.__file__   :", cv2.__file__)

    # # show key build flags
    # bi = cv2.getBuildInformation().splitlines()
    # for line in bi:
    #     if any(k in line for k in ("Video I/O", "FFMPEG:", "GStreamer:", "VA:", "libva", "VAAPI", "avcodec", "avformat")):
    #         print(line)

    # # show which libav* are actually linked/loaded for this cv2
    # sh("bash", "-lc", f"ldd {cv2.__file__} | grep -E 'avcodec|avformat|avutil|swscale|va|drm' || true")

    # print_section("3) OpenCV read tests: default / software-only / VAAPI-forced")
    # def try_capture(name: str, cap: "cv2.VideoCapture") -> None:
    #     print(f"\n--- {name} ---")
    #     print("opened:", cap.isOpened())
    #     if not cap.isOpened():
    #         cap.release()
    #         return
    #     fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
    #     fcc = "".join(chr((fourcc >> 8*i) & 0xFF) for i in range(4))
    #     print("fourcc:", repr(fcc), fourcc)
    #     ok, compressed_frame = cap.read()
    #     print("read:", ok, None if compressed_frame is None else compressed_frame.shape)
    #     cap.release()

    # # More verbose OpenCV videoio logging (may or may not print depending on build)
    # os.environ.setdefault("OPENCV_VIDEOIO_DEBUG", "1")

    # # A) Default (whatever OpenCV decides)
    # try_capture("A) default CAP_FFMPEG", cv2.VideoCapture(VIDEO, cv2.CAP_FFMPEG))

    # # B) Force software (disable HW accel)
    # try:
    #     cap = cv2.VideoCapture(
    #         VIDEO,
    #         cv2.CAP_FFMPEG,
    #         (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_NONE),
    #     )
    #     try_capture("B) software-only (VIDEO_ACCELERATION_NONE)", cap)
    # except Exception as e:
    #     print("B) software-only: exception:", e)

    # # C) Force VAAPI
    # try:
    #     cap = cv2.VideoCapture(
    #         VIDEO,
    #         cv2.CAP_FFMPEG,
    #         (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_VAAPI),
    #     )
    #     try_capture("C) VAAPI-forced (VIDEO_ACCELERATION_VAAPI)", cap)
    # except Exception as e:
    #     print("C) VAAPI-forced: exception:", e)

    # print_section("4) Extra: Increase probe/analyze duration for OpenCV+FFmpeg (optional)")
    # print("If you still see 'Missing Sequence Header', try running the next cell first:")
    # print('os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "analyzeduration;5000000|probesize;5000000"')
    return


@app.cell
def _(video_dir):
    import cv2
    path = str(video_dir / "better-video-qualityDoug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.15mb.webm")

    cap = cv2.VideoCapture(
        path,
        cv2.CAP_FFMPEG,
        [cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_VAAPI],
    )
    return (cv2,)


@app.cell
def _(cv2):
    import os, sys
    print("cv2.__file__ =", getattr(cv2, "__file__", None))
    print("cwd          =", os.getcwd())
    print("has VideoCapture:", hasattr(cv2, "VideoCapture"))
    print("has imread     :", hasattr(cv2, "imread"))
    return (sys,)


@app.cell
def _(cv2):
    print(cv2.getBuildInformation())
    return


@app.cell
def _(sys):
    print(sys.executable)
    return


@app.cell
def _():
    # # import cv2

    # # video = str(video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0-av1_15mb_audio.webm")
    # video = str(video_dir / "better-video-qualityDoug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.15mb.webm")
    # # video = str(video_dir / "output.mp4")
    # t_sec = 5.2

    # cap = cv2.VideoCapture(video)
    # cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)

    # ok, compressed_frame_bgr = cap.read()
    # cap.release()

    # if not ok:
    #     raise RuntimeError("Could not read compressed_frame")
    return


@app.cell
def _():
    # cv2.imwrite("compressed_frame_5.2s.png", compressed_frame_bgr)

    # t_sec = 5.2

    # cap = cv2.VideoCapture(video)
    # cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)

    # ok, compressed_frame_bgr = cap.read()
    # cap.release()

    # if not ok:
    #     raise RuntimeError("Could not read compressed_frame")

    # cv2.imwrite("compressed_frame_5.2s.png", compressed_frame_bgr)
    return


@app.cell
def _():
    return


@app.cell(column=1, hide_code=True)
def _(mo):
    mo.md(r"""
    # test with a vison language model
    """)
    return


@app.cell
def _(compressed_frame):
    compressed_frame.as_posix()
    return


@app.cell
def _():
    # Load and run the model:
    # llama-server -hf unsloth/Qwen3-VL-2B-Instruct-GGUF:Q4_K_M
    # Load and run the model:
    # llama-server -hf unsloth/Qwen3-VL-2B-Instruct-GGUF:Q3_K_S
    return


@app.cell
def _():
    # curl http://localhost:1234/v1/chat/completions \
    #   -H "Content-Type: application/json" \
    #   -d '{
    #     "model": "qwen/qwen3-vl-8b",
    #     "messages": [
    #         {
    #             "role": "system",
    #             "content": "Always answer in rhymes. Today is Thursday"
    #         },
    #         {
    #             "role": "user",
    #             "content": "What day is it today?"
    #         }
    #     ],
    #     "temperature": 0.7,
    #     "max_tokens": -1,
    #     "stream": false
    # }'
    return


@app.cell
def _(compressed_frame, mo):
    mo.image(compressed_frame.as_posix())
    return


@app.cell
def _():
    import base64
    from openai import OpenAI

    def image_file_to_data_url(path: str) -> str:
        # Change mime if needed: image/jpeg, image/webp, etc.
        mime = "image/png"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:{mime};base64,{b64}"

    client = OpenAI(
        base_url="http://localhost:1234/v1",  # or http://localhost:8000/v1
        api_key="unused",  # many local servers ignore this
    )
    return client, image_file_to_data_url


@app.cell
def _(Markdown, client, compressed_frame, image_file_to_data_url):
    resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what you see. If there is text, transcribe it."},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(compressed_frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )

    Markdown(resp.choices[0].message.content)
    return (resp,)


@app.cell
def _(resp):
    print(resp.choices[0].message.content)
    return


@app.cell
def _(mo):
    mo.md(r"""
    This image is a screenshot from a live-streamed video, likely from a Twitch or similar platform, showing a person (a streamer) and a large map of Europe.

    Here's a breakdown of what is visible:

    **1. The Streamer (Left Side):**
    *   A man with short brown hair and a beard is sitting at a desk.
    *   He is wearing headphones and speaking into a large, professional microphone.
    *   He appears focused, looking down at his desk or screen.
    *   On his desk, there are a few books stacked together and a small orange figurine with large eyes.

    **2. The Map (Right Side):**
    *   A large, high-resolution map of Europe is displayed on a screen behind the streamer.
    *   The map shows the political boundaries of European countries.
    *   The countries are labeled with their names, including:
        *   **Northern Europe:** Iceland, Norway, Sweden, Finland, Denmark, Estonia, Latvia, Lithuania, Russia.
        *   **Western Europe:** Ireland, Britain, Netherlands, Belgium, France, Switzerland, Germany, Austria, Czech Republic, Slovakia, Poland.
        *   **Southern Europe:** Italy, Spain, Portugal, Greece, Turkey, Bulgaria, Romania, Serbia, Hungary, Croatia, Slovenia, Bosnia and Herzegovina, Montenegro, North Macedonia, Albania.
    *   Some areas, like the Baltic Sea, the North Sea, the Black Sea, and the Mediterranean Sea, are colored light blue, indicating water.

    **3. Text and Chat (Left Side):**
    *   A live chat window is visible on the left side of the screen.
    *   The chat contains comments from viewers, some of which are humorous or related to a specific event (e.g., "So when Doug won't open the oxygen gates, we have to rely on the fart barons").
    *   A user named "iamkaalhode" is actively participating in the conversation.

    **4. Text Overlay (Bottom Right):**
    *   At the bottom right of the screen, there is a text overlay that reads:
        > PARKZER Q&A
        > Stop donating so I can leave

    This suggests the streamer is currently hosting a Q&A session with a viewer named "PARKZER" and is humorously asking viewers to stop donating so he can leave the stream.
    """)
    return


@app.cell
def _():
    return


@app.cell(column=2)
def _(mo):
    mo.md(r"""
    # tests with chat extraction
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## using a compressed frame
    """)
    return


@app.cell
def _(Markdown, client, compressed_frame, image_file_to_data_url):
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Get all the chat messages. Please also include usernames with messages"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(compressed_frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )

    Markdown(_resp.choices[0].message.content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## using the source frame
    """)
    return


@app.cell
def _(Markdown, client, image_file_to_data_url, source_frame):
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Get all the chat messages. Please also include usernames with messages"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(source_frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )
    print(_resp.choices[0].message.content)
    Markdown(_resp.choices[0].message.content)
    return


@app.cell
def _(Markdown, client, image_file_to_data_url, source_frame):
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Get all the chat messages. Please also include usernames with messages, when performing the extraction, replace emojis with `:oneworddescriptionofemoji:`"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(source_frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )
    print(_resp.choices[0].message.content)
    Markdown(_resp.choices[0].message.content)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## experiments with getting pixel position
    """)
    return


@app.cell
def _(Markdown, client, compressed_frame, image_file_to_data_url):
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Give me the pixel position of 'corriellintric: I have 80 cakes on the table'"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(compressed_frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )

    Markdown(_resp.choices[0].message.content)
    return


@app.cell
def _(Markdown, client, image_file_to_data_url, supporting_files):
    next_example = supporting_files / "images" / "2026-01-12" / "20260112200709.png"
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Give me the pixel position of 'corriellintric: I have 80 cakes on the table'"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(next_example.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )

    Markdown(_resp.choices[0].message.content)
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## using a structured output for a batch of 8 images
    """)
    return


@app.cell
def _(List, supporting_files):
    import mimetypes
    from pydantic import BaseModel, Field


    # ---------- config ----------
    FRAMES_DIR = supporting_files / "data" / "cropped_kf_cache_test"
    # MODEL = "qwen/qwen3-vl-8b" 
    # MODEL = "lmstudio-community/Qwen3-VL-8B-Instruct-GGUF"
    MODEL = "lmstudio-community/Qwen3-VL-30B-A3B-Instruct-GGUF"
    BASE_URL = "http://localhost:1234/v1"
    API_KEY = "unused"


    # ---------- helpers ----------
    # def image_file_to_data_url(path: str | Path) -> str:
    #     p = Path(path)
    #     mime, _ = mimetypes.guess_type(str(p))
    #     mime = mime or "image/jpeg"
    #     with p.open("rb") as f:
    #         b64 = base64.b64encode(f.read()).decode("utf-8")
    #     return f"data:{mime};base64,{b64}"


    # ---------- structured output ----------
    class EmoteBox(BaseModel):
        x: int = Field(..., description="Top-left X coordinate of the emote bounding box (pixels, image coordinate space).")
        y: int = Field(..., description="Top-left Y coordinate of the emote bounding box (pixels, image coordinate space).")
        w: int = Field(..., description="Width of the emote bounding box (pixels).")
        h: int = Field(..., description="Height of the emote bounding box (pixels).")
        description: str = Field(..., description="Short human-readable description of the emote (e.g., 'PepeHands', 'Luigi'). use a full description rather than a the emoji shorthand")


    class ChatMessage(BaseModel):
        user_name: str = Field(..., description="Username as shown in the chat UI for this line (no inferred/extra metadata).")
        message: str = Field(..., description="Visible message text and emoji (described as 1 word) for this chat line. If emotes and emojis are in the message, include them inline and use a structure of `:emote_described:` `:another_emote_described:` ...")
        emotes: List[EmoteBox] = Field(
            default_factory=list,
            description="List of emotes found on this chat line, each with an approximate bounding box in pixels. ",
        )


    class ImageOnlyExtraction(BaseModel):
        chat_messages: List[ChatMessage] = Field(
            default_factory=list,
            description="All visible chat lines in a single image, in top-to-bottom reading order.",
        )


    class BatchExtraction(BaseModel):
        images: List[ImageOnlyExtraction] = Field(
            ...,
            description="Exactly 8 per-image extractions, in the same order as the 8 input images.",
        )
    return BatchExtraction, FRAMES_DIR, MODEL


@app.cell
def _(FRAMES_DIR, image_file_to_data_url):
    # ---------- pick first 8 files ----------
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    files = sorted([p for p in FRAMES_DIR.iterdir() if p.is_file() and p.suffix.lower() in exts])[:8]
    if len(files) < 8:
        raise RuntimeError(f"Need at least 8 images in {FRAMES_DIR.resolve()}, found {len(files)}")

    content = [
        {
            "type": "text",
            "text": (
                "You will receive multiple chat screenshots with overlapping messages"
                "Return ONLY JSON matching the provided schema."
                "For each image, extract ALL new unique visible chat lines."
                "Include usernames + message text and emotes/emojis. If message text is not visible, use '(No message text visible)'."
                "For each message line, list any emotes with approximate bounding boxes in pixels."
                "When detecting and writing emotes/emojis, use the structure of `:describe_this_emoji:`"
                "When emojis are detected in a message, please include the 1 word description in the structure  `:emojidescription:` in the message, do not remove it from the message"
                "For example: 'I like this song :dancefrog: :dancefrog: it's the best', use the emote/emoji description in the message"
                # "Coordinates: x,y are top-left; w,h are width/height. Use integers."
                # ""
                # "IMAGES METADATA (echo these fields back exactly per image):"
            ),
        }
    ]

    for p in files:
        image_unique_id = p.stem  # e.g., "kf_000010_22.550s"
        content.append({"type": "text", "text": f"IMAGE_START {image_unique_id}"})
        content.append({"type": "image_url", "image_url": {"url": image_file_to_data_url(p)}})

    messages = [{"role": "user", "content": content}]
    return messages, p


@app.cell
def _(messages):
    messages
    return


@app.cell
def _(BatchExtraction, MODEL, client, messages):
    # Preferred: structured parse (if your server supports it)
    compact_resp = client.beta.chat.completions.parse(
        model=MODEL,
        response_format=BatchExtraction,
        messages=messages,
        temperature=0.2,
        max_tokens=-1,
    )

    compact_parsed = compact_resp.choices[0].message.parsed
    compact_batch = BatchExtraction.model_validate(compact_parsed)

    print(compact_batch.model_dump_json(indent=2))
    return


@app.cell
def _():
    previous_compact_resp = {
      "images": [
        {
          "chat_messages": [
            {
              "user_name": "ToaSTy_T0aST",
              "message": "nvm its on a cooldown",
              "emotes": [
                {
                  "x": 240,
                  "y": 20,
                  "w": 30,
                  "h": 30,
                  "description": "green frog"
                }
              ]
            },
            {
              "user_name": "frickelodeon",
              "message": "@iamkaalhode believe in the doubt",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "red heart"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "speaker"
                }
              ]
            },
            {
              "user_name": "sour_appel",
              "message": "So when Doug won't open the oxygen gates, we have to rely on the fart barons",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "red heart"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "whamer100",
              "message": "yeah why is the prediction open for so long",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "frickelodeon",
              "message": "@iamkaalhode believe in the doubt",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "red heart"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "speaker"
                }
              ]
            },
            {
              "user_name": "sour_appel",
              "message": "So when Doug won't open the oxygen gates, we have to rely on the fart barons",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "red heart"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "whamer100",
              "message": "yeah why is the prediction open for so long",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "sour_appel",
              "message": "So when Doug won't open the oxygen gates, we have to rely on the fart barons",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "red heart"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "whamer100",
              "message": "yeah why is the prediction open for so long",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "whamer100",
              "message": "yeah why is the prediction open for so long",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "TheHolyPangolin",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "@whamer100 Because RIGGED",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "orange owl"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "question mark"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        },
        {
          "chat_messages": [
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": [
                {
                  "x": 10,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 30,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 50,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 70,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                },
                {
                  "x": 90,
                  "y": 10,
                  "w": 20,
                  "h": 20,
                  "description": "green mario"
                }
              ]
            }
          ]
        }
      ]
    }
    previous_compact_resp
    return


@app.cell
def _():
    qwen3_vl_30b_resp = {
      "images": [
        {
          "chat_messages": [
            {
              "user_name": "ToaSTy_T0aST",
              "message": "nvm its on a cooldown :frog:",
              "emotes": [
                {
                  "x": 51,
                  "y": 46,
                  "w": 23,
                  "h": 23,
                  "description": "frog"
                }
              ]
            },
            {
              "user_name": "frickelodeon",
              "message": "@iamkaalhode believe in the doubt",
              "emotes": []
            },
            {
              "user_name": "sour_apple",
              "message": "So when Doug won't open the oxygen gates, we have to rely on the fart barons",
              "emotes": []
            },
            {
              "user_name": "whamer100",
              "message": "yeah why is the prediction open for so long",
              "emotes": []
            },
            {
              "user_name": "iamkaalhode",
              "message": "I have betted too much to lose D.",
              "emotes": []
            },
            {
              "user_name": "Gavyn_J",
              "message": "",
              "emotes": [
                {
                  "x": 58,
                  "y": 297,
                  "w": 30,
                  "h": 30,
                  "description": "man with glasses"
                }
              ]
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "@whamer100 Because RIGGED",
              "emotes": []
            },
            {
              "user_name": "Komodo66619",
              "message": ":mario: :mario: :mario: :mario:",
              "emotes": [
                {
                  "x": 25,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 40,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 56,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 72,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                }
              ]
            },
            {
              "user_name": "comicallyidiotic",
              "message": "I have 80 cakes on the table",
              "emotes": []
            },
            {
              "user_name": "Jennie027",
              "message": "the strat was to wait until doug goes live or doesn't because the prediction goes past the time",
              "emotes": []
            },
            {
              "user_name": "projectdolphin_",
              "message": "",
              "emotes": [
                {
                  "x": 58,
                  "y": 596,
                  "w": 30,
                  "h": 30,
                  "description": "man with glasses"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "crismanti20",
              "message": "EUROPE :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 567,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "He changed title",
              "emotes": []
            },
            {
              "user_name": "pegglequeen1",
              "message": "why is the prediction this long? people will just wait to doubt",
              "emotes": []
            },
            {
              "user_name": "meowsticks24",
              "message": "DOUG",
              "emotes": []
            },
            {
              "user_name": "iamkaalhode",
              "message": "NOOOOOOO",
              "emotes": []
            },
            {
              "user_name": "Jennie027",
              "message": "FUCK YEAH",
              "emotes": []
            },
            {
              "user_name": "nora_bot",
              "message": "",
              "emotes": [
                {
                  "x": 58,
                  "y": 196,
                  "w": 30,
                  "h": 30,
                  "description": "man with glasses"
                }
              ]
            },
            {
              "user_name": "whamer100",
              "message": "fuck",
              "emotes": []
            },
            {
              "user_name": "mmust_m",
              "message": "YESSSSSSSSS",
              "emotes": []
            },
            {
              "user_name": "DatKirby_",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "bananaz602",
              "message": "LES GO :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 318,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": ":mario: :mario: :mario:",
              "emotes": [
                {
                  "x": 25,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 40,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 56,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                }
              ]
            },
            {
              "user_name": "Evening_Owl",
              "message": "YES :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "DOUG :mario: :mario:",
              "emotes": [
                {
                  "x": 135,
                  "y": 420,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 151,
                  "y": 420,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                }
              ]
            },
            {
              "user_name": "Sky0nn",
              "message": "YEEAAH BELIEVERS :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 452,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Jennie027",
              "message": "I AM THE GREATEST :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 486,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "KimbolineNorway",
              "message": "Doug! :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 520,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "BradS18",
              "message": "LETS GOOOO :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 552,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Evening_Owl",
              "message": "BELIEVERS WIN :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 586,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "projectdolphin_",
              "message": "FUCK :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 620,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "mrgundhamtanaka",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "NOOOOOOOOO",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "whamer100",
              "message": "DOUG MY MONEY :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "moomin_tophat",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "tacoespionage",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "meowsticks24",
              "message": "GEOGRAPHY :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "crismanti20",
              "message": "Yo :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Jennie027",
              "message": "I AM SO GOOD AT BETTING :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 486,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "LankLTE",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "mmust_m",
              "message": "SUCK IT NON BELIEVERS :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "Yeeesssssssssss",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "mrgundhamtanaka",
              "message": "RIGGged :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "_d_dip",
              "message": "NOOOO :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "dinklebergle",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "comicallyidiotic",
              "message": "NOOOOO :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "BradS18",
              "message": "DOUGGGG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Duarpeto",
              "message": "DOOOOOOG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "pegglequeen1",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "nora_bot",
              "message": "IT WAS ALL WORTH IT :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": ":frog: :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 51,
                  "y": 284,
                  "w": 23,
                  "h": 23,
                  "description": "frog"
                },
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Evening_Owl",
              "message": "STOP DONATING :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "SO HE CAN LEAVE",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "TheHolyPangolin",
              "message": "DOUG DOUG :mario: :mario:",
              "emotes": [
                {
                  "x": 135,
                  "y": 420,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 151,
                  "y": 420,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                }
              ]
            },
            {
              "user_name": "Komodo66619",
              "message": ":mario: :mario: :mario:",
              "emotes": [
                {
                  "x": 25,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 40,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                },
                {
                  "x": 56,
                  "y": 387,
                  "w": 14,
                  "h": 14,
                  "description": "mario"
                }
              ]
            },
            {
              "user_name": "gforce_gaming_official",
              "message": "FINALLY :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "mmust_m",
              "message": "SHUN THE NON-BELIEVERS :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "toughrobotics",
              "message": "Don't stream today :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "FlyignPig",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "iamkaalhode",
              "message": "I lost 16k :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "tacoespionage",
              "message": "PREDICTION RIGGED :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Jennie027",
              "message": "I AM THE GREATEST PREDICTOR IN THE HISTORY OF PREDICTIONS :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 486,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "tacoespionage",
              "message": "REFUND :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "BradS18",
              "message": "GIVE ME MY MONEY :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "heidi_susanna",
              "message": "DOUG :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "Sky0nn",
              "message": "But now since prediction was :face_with_tears_of_joy:",
              "emotes": [
                {
                  "x": 135,
                  "y": 284,
                  "w": 14,
                  "h": 14,
                  "description": "face with tears of joy"
                }
              ]
            },
            {
              "user_name": "dinkiebergle",
              "message": "",
              "emotes": []
            },
            {
              "user_name": "tacoespionage",
              "message": "",
              "emotes": []
            }
          ]
        }
      ]
    }
    qwen3_vl_30b_resp
    return


@app.cell
def _():
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## using structured output for a single image
    I wanted to compare a single image vs a batch (duration and accuracy)
    """)
    return


@app.cell
def _():
    return


@app.cell(column=3, hide_code=True)
def _(mo):
    mo.md(r"""
    # testing compressed_frame extraction
    This was my first attempt at trying to track how far a single message tracked. It's a idea to revisit if keyframe extraction doesn't work
    """)
    return


@app.cell
def _():
    # from __future__ import annotations

    # from dataclasses import dataclass
    # from typing import Optional, Tuple

    # # import cv2
    # import numpy as np


    # @dataclass(frozen=True)
    # class MatchResult:
    #     timestamp_s: float
    #     score: float
    #     y_in_chat_px: int
    #     x_in_chat_px: int


    # def find_chat_template_reaches_top(
    #     video_path: str,
    #     template_path: str,
    #     chat_rect: Tuple[int, int, int, int],  # (x, y, w, h) in video pixels
    #     *,
    #     top_px: int = 12,
    #     sample_fps: float = 10.0,
    #     match_thr: float = 0.80,
    #     start_s: float = 0.0,
    #     end_s: float = 0.0,  # 0 = scan to end
    #     blur: bool = True,
    # ) -> Optional[MatchResult]:
    #     """
    #     Finds the first timestamp where the given template (e.g., a specific chat line)
    #     is detected within the chat crop and its top-left Y position is <= top_px.

    #     Returns MatchResult if found; otherwise None.
    #     """
    #     tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    #     if tmpl is None or tmpl.size == 0:
    #         raise ValueError(f"Could not read template: {template_path}")

    #     cap = cv2.VideoCapture(video_path)
    #     if not cap.isOpened():
    #         raise ValueError(f"Could not open video: {video_path}")

    #     video_fps = cap.get(cv2.CAP_PROP_FPS)
    #     if not video_fps or video_fps <= 0:
    #         video_fps = 30.0

    #     # Process every Nth compressed_frame to approximate sample_fps
    #     step = max(1, int(round(video_fps / max(sample_fps, 0.1))))

    #     x, y, w, h = chat_rect
    #     if w <= 0 or h <= 0:
    #         raise ValueError("chat_rect must have positive w and h")

    #     if start_s > 0:
    #         cap.set(cv2.CAP_PROP_POS_MSEC, start_s * 1000.0)

    #     # Pre-blur template once if requested
    #     if blur:
    #         tmpl_proc = cv2.GaussianBlur(tmpl, (3, 3), 0)
    #     else:
    #         tmpl_proc = tmpl

    #     compressed_frame_idx = 0
    #     while True:
    #         t_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
    #         if end_s > 0 and t_s > end_s:
    #             break

    #         ok, compressed_frame = cap.read()
    #         if not ok:
    #             break

    #         if compressed_frame_idx % step != 0:
    #             compressed_frame_idx += 1
    #             continue
    #         compressed_frame_idx += 1

    #         chat = compressed_frame[y : y + h, x : x + w]
    #         if chat.size == 0:
    #             raise ValueError("chat_rect is out of bounds for this video compressed_frame size")

    #         gray = cv2.cvtColor(chat, cv2.COLOR_BGR2GRAY)
    #         if blur:
    #             gray = cv2.GaussianBlur(gray, (3, 3), 0)

    #         # Template matching
    #         res = cv2.matchTemplate(gray, tmpl_proc, cv2.TM_CCOEFF_NORMED)
    #         _, max_val, _, max_loc = cv2.minMaxLoc(res)  # max_loc = (x, y) in chat crop

    #         if max_val >= match_thr:
    #             mx, my = int(max_loc[0]), int(max_loc[1])
    #             if my <= top_px:
    #                 return MatchResult(timestamp_s=float(t_s), score=float(max_val), y_in_chat_px=my, x_in_chat_px=mx)

    #     return None
    return


@app.cell
def _():
    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Optional, Tuple
    import subprocess
    import numpy as np

    try:
        from PIL import Image
    except Exception as e:
        raise RuntimeError("Pillow is required for template loading: pip install pillow") from e


    @dataclass(frozen=True)
    class MatchResult:
        timestamp_s: float
        score: float
        y_in_chat_px: int


    def find_chat_template_reaches_top_noopencv(
        video_path: str,
        template_path: str,
        chat_rect: Tuple[int, int, int, int],  # (x, y, w, h) in *video* pixels
        *,
        x0: int = 0,              # fixed X inside chat crop where the line starts (usually 0)
        top_px: int = 12,         # trigger when matched y <= top_px
        search_height: int = 280, # only search within top N pixels of chat crop
        sample_fps: float = 10.0, # how often to sample compressed_frames
        match_thr: float = 0.80,  # NCC threshold
        start_s: float = 0.0,
        end_s: float = 0.0,       # 0 = until end
    ) -> Optional[MatchResult]:
        """
        Streams cropped compressed_frames via ffmpeg and finds when `template_path` (a cropped image of the chat line)
        reaches near the top of the chat crop.

        Returns first MatchResult found, else None.

        Requirements:
          - ffmpeg in PATH
          - numpy
          - pillow
        """

        # Load template as grayscale float32
        tmpl_u8 = np.array(Image.open(template_path).convert("L"), dtype=np.uint8)
        th, tw = tmpl_u8.shape[:2]
        tmpl = tmpl_u8.astype(np.float32)
        tmpl_z = tmpl - tmpl.mean()
        tmpl_norm = float(np.sqrt((tmpl_z * tmpl_z).sum()) + 1e-6)

        x, y, w, h = map(int, chat_rect)
        if tw + x0 > w:
            raise ValueError(f"Template width {tw} (plus x0={x0}) exceeds chat crop width {w}")
        if th > h:
            raise ValueError(f"Template height {th} exceeds chat crop height {h}")

        H = min(int(search_height), h)
        if H < th:
            raise ValueError(f"search_height {H} is smaller than template height {th}")

        # ffmpeg: crop chat area, sample fps, grayscale, output raw compressed_frames
        vf = f"crop={w}:{h}:{x}:{y},fps={sample_fps},format=gray"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
        if start_s > 0:
            cmd += ["-ss", str(start_s)]
        cmd += ["-i", video_path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdout is not None

        compressed_frame_bytes = w * h
        compressed_frame_index = 0

        # Use sliding_window_view for vectorized Y-only search (X fixed by taking width=tw slice)
        sliding_window_view = np.lib.stride_tricks.sliding_window_view

        try:
            while True:
                if end_s > 0:
                    # Approximate timestamp based on sampled compressed_frames
                    t_s = start_s + (compressed_frame_index / sample_fps)
                    if t_s > end_s:
                        break

                buf = proc.stdout.read(compressed_frame_bytes)
                if len(buf) != compressed_frame_bytes:
                    break

                compressed_frame_index += 1
                compressed_frame = np.frombuffer(buf, dtype=np.uint8).reshape((h, w))
                band = compressed_frame[:H, :]  # top search band

                roi = band[:, x0 : x0 + tw]  # (H, tw)

                # Windows along Y only (x dimension is fixed because roi width == tw)
                # shape: (H-th+1, 1, th, tw) -> squeeze -> (H-th+1, th, tw)
                windows = sliding_window_view(roi, (th, tw))[:, 0, :, :].astype(np.float32)

                # Normalized cross-correlation per Y
                win_mean = windows.mean(axis=(1, 2), keepdims=True)
                win_z = windows - win_mean
                num = (win_z * tmpl_z).sum(axis=(1, 2))
                den = np.sqrt((win_z * win_z).sum(axis=(1, 2))) * tmpl_norm + 1e-6
                scores = num / den

                best_y = int(scores.argmax())
                best_score = float(scores[best_y])

                if best_score >= match_thr and best_y <= top_px:
                    # Timestamp is approximate based on fps sampling; good enough for compressed_frame extraction
                    ts = start_s + ((compressed_frame_index - 1) / sample_fps)
                    return MatchResult(timestamp_s=float(ts), score=best_score, y_in_chat_px=best_y)

        finally:
            try:
                proc.stdout.close()
            except Exception:
                pass
            proc.wait()

        return None


    # References (in-code per request):
    # - ffmpeg filters: https://ffmpeg.org/ffmpeg-filters.html
    # - ffmpeg rawvideo muxer: https://ffmpeg.org/ffmpeg-formats.html#rawvideo
    # - numpy sliding_window_view: https://numpy.org/doc/stable/reference/generated/numpy.lib.stride_tricks.sliding_window_view.html
    return (
        Image,
        Optional,
        dataclass,
        find_chat_template_reaches_top_noopencv,
        np,
        subprocess,
    )


@app.cell
def _(compressed_frame, find_chat_template_reaches_top_noopencv, video_dir):
    res = find_chat_template_reaches_top_noopencv(
        video_path=str(video_dir / "better-video-qualityDoug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.15mb.webm"),
        template_path=compressed_frame,
        chat_rect=(0, 40, 360, 900),  # replace with your chat crop
        x0=0,
        top_px=12,
        search_height=260,
        sample_fps=10,
        match_thr=0.85,
    )
    return


@app.cell
def _():
    return


@app.cell(column=4, hide_code=True)
def _(mo):
    mo.md(r"""
    # keyframe extraction
    """)
    return


@app.cell
def _(Path):
    import json
    import re
    from dataclasses import asdict
    from typing import Union

    PathLike = Union[str, Path]
    return PathLike, asdict, json, re


@app.cell
def _(Optional, Path, PathLike, asdict, dataclass, json, re, subprocess):

    @dataclass
    class KeyframeReport:
        input: str
        stream: str
        mode_used: str                 # "packets" or "frames"
        keyframes: int
        timestamps: list[float]        # seconds
        intervals: Optional[dict[str, float]]  # {"min":..., "avg":..., "max":...} or None
        output: str


    def _safe_stem(name: str) -> str:
        # spaces -> underscores; weird chars -> underscores
        name = name.replace(" ", "_")
        name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
        name = re.sub(r"_+", "_", name).strip("._-")
        return name or "report"


    def _resolve_output_path(input_file: Path, output_path: Path) -> Path:
        # If output_path is an existing directory, write into it.
        if output_path.exists() and output_path.is_dir():
            return output_path / f"{_safe_stem(input_file.stem)}_keyframes_report.json"

        # If output_path has a suffix, treat as explicit file path.
        if output_path.suffix:
            return output_path

        # Otherwise treat as a directory path (even if it doesn't exist yet).
        return output_path / f"{_safe_stem(input_file.stem)}_keyframes_report.json"


    def _run(cmd: list[str]) -> str:
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return p.stdout
        except FileNotFoundError as e:
            raise RuntimeError("ffprobe/ffmpeg not found on PATH.") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\n\n{e.stderr.strip()}") from e


    def _parse_packets_pts(csv_text: str) -> list[float]:
        # CSV: "<pts_time>,<dts_time>,<flags>"
        ts: list[float] = []
        for line in csv_text.splitlines():
            line = line.strip()
            if not line:
                continue
            pts_s, dts_s, flags = [p.strip() for p in line.split(",", 2)]
            if "K" not in flags:
                continue

            t_s = pts_s if pts_s not in ("N/A", "", "nan") else dts_s
            if t_s in ("N/A", "", "nan"):
                continue

            ts.append(float(t_s))
        return ts


    def _parse_frames_ts(csv_text: str) -> list[float]:
        # CSV: "<best_effort_timestamp_time>,<key_frame>"
        ts: list[float] = []
        for line in csv_text.splitlines():
            line = line.strip()
            if not line:
                continue
            t_s, key_s = [p.strip() for p in line.split(",", 1)]
            if key_s != "1":
                continue
            if t_s in ("N/A", "", "nan"):
                continue
            ts.append(float(t_s))
        return ts


    def keyframe_report(input_path: PathLike, output_path: PathLike, stream: str = "v:0") -> KeyframeReport:
        """
        Produces keyframe timestamps (seconds) and writes a JSON report.

        output_path behavior:
          - If output_path is an existing directory OR has no suffix:
              <output_path>/<input_stem_sanitized>_keyframes_report.json
          - If output_path has a suffix (e.g. .json): writes exactly there
        """
        in_p = Path(input_path)
        if not in_p.exists():
            raise FileNotFoundError(f"Input not found: {in_p}")
        if not in_p.is_file():
            raise ValueError(f"Input must be a file: {in_p}")

        out_p = _resolve_output_path(in_p, Path(output_path))
        out_p.parent.mkdir(parents=True, exist_ok=True)

        # Fast path: packets (no decode)
        pkt_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", stream,
            "-show_packets",
            "-show_entries", "packet=pts_time,dts_time,flags",
            "-of", "csv=p=0",
            str(in_p),
        ]
        pkt_out = _run(pkt_cmd)
        timestamps = _parse_packets_pts(pkt_out)
        mode_used = "packets"

        # Fallback: frames (slower, but reliable if packet flags/timestamps are weird)
        if not timestamps:
            frm_cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", stream,
                "-skip_frame", "nokey",  # only keyframes
                "-show_frames",
                "-show_entries", "frame=best_effort_timestamp_time,key_frame",
                "-of", "csv=p=0",
                str(in_p),
            ]
            frm_out = _run(frm_cmd)
            timestamps = _parse_frames_ts(frm_out)
            mode_used = "frames"

        # sort + de-dupe (rounded to avoid float jitter)
        timestamps = sorted({round(t, 6) for t in timestamps})

        intervals: Optional[dict[str, float]] = None
        if len(timestamps) >= 2:
            diffs = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
            intervals = {"min": min(diffs), "avg": sum(diffs) / len(diffs), "max": max(diffs)}

        report = KeyframeReport(
            input=str(in_p),
            stream=stream,
            mode_used=mode_used,
            keyframes=len(timestamps),
            timestamps=timestamps,
            intervals=intervals,
            output=str(out_p),
        )

        out_p.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
        return report


    def extract_keyframes(
        input_path: PathLike,
        timestamps: list[float],
        output_dir: PathLike,
        limit: Optional[int] = None,
        ext: str = "jpg",
        qv: int = 2,  # ffmpeg -q:v (lower is better for jpg)
    ) -> list[Path]:
        """
        Extract images at the provided timestamps using ffmpeg -ss.
        Returns the list of written files.
        """
        in_p = Path(input_path)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        ts_iter = timestamps if limit is None else timestamps[:limit]

        for i, t in enumerate(ts_iter, start=1):
            out_file = out_dir / f"keyframe_{i:06d}_{t:.3f}s.{ext.lstrip('.')}"
            _run([
                "ffmpeg", "-v", "error",
                "-ss", f"{t:.6f}",
                "-i", str(in_p),
                "-frames:v", "1",
                "-q:v", str(qv),
                str(out_file),
            ])
            written.append(out_file)

        return written
    return (keyframe_report,)


@app.cell
def _(video_dir):
    ai_invasion_1 = video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.mkv"
    ai_invasion_1
    return (ai_invasion_1,)


@app.cell
def _(ai_invasion_1, data_dir, keyframe_report):
    doug_report = keyframe_report(ai_invasion_1 , data_dir)
    return


@app.cell
def _(json, supporting_files):
    doug_report_fp = supporting_files / "data" / "Doug_and_Twitch_Chat_TAKE_OVER_EUROPE-VpmmuHlLPM0_keyframes_report.json"

    with open(doug_report_fp, "r", encoding="utf-8") as _f:
        doug_report_dict = json.load(_f)
    return doug_report_dict, doug_report_fp


@app.cell
def _(doug_report_dict):
    doug_report_dict
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## inspecting frames
    """)
    return


@app.cell
def _(ai_invasion_1, doug_report_fp, supporting_files):
    import io
    from functools import lru_cache
    # marimo app: jump through keyframes by index, extract & display the selected keyframe
    # Requires: ffmpeg on PATH, and a keyframe_report JSON with "timestamps"

    # ---------- config ----------
    VIDEO_PATH = ai_invasion_1
    REPORT_JSON = doug_report_fp 
    CACHE_DIR = supporting_files / "data" / "keyframe_cache"
    return CACHE_DIR, REPORT_JSON, VIDEO_PATH


@app.cell
def _(Path, REPORT_JSON, json):
    # Cell 2: load timestamps

    def load_timestamps(report_json: Path) -> list[float]:
        rep = json.loads(report_json.read_text(encoding="utf-8"))
        ts = rep.get("timestamps", [])
        if not isinstance(ts, list) or not ts:
            raise ValueError("Report JSON has no timestamps.")
        return [float(x) for x in ts]

    timestamps = load_timestamps(REPORT_JSON)
    n = len(timestamps)
    return load_timestamps, n


@app.cell
def _(Path, subprocess):
    # Cell 3: cached extraction

    def extract_frame_at_ts(video: Path, t: float, out_file: Path) -> Path:
        out_file.parent.mkdir(parents=True, exist_ok=True)
        if out_file.exists():
            return out_file

        subprocess.run(
            [
                "ffmpeg",
                "-v", "error",
                "-ss", f"{t:.6f}",
                "-i", str(video),
                "-frames:v", "1",
                "-q:v", "2",
                str(out_file),
            ],
            check=True,
        )
        return out_file
    return (extract_frame_at_ts,)


@app.cell
def _(mo, n):
    # Cell 4: state (index + jump)

    get_idx, set_idx = mo.state(0)
    get_jump, set_jump = mo.state(0)

    def clamp_index(v: int) -> int:
        return max(0, min(n - 1, int(v)))
    return clamp_index, get_idx, get_jump, set_idx, set_jump


@app.cell
def _(clamp_index, get_idx, mo, n, set_idx):
    # Cell 5 (UI): slider bound to state

    slider = mo.ui.slider(
        start=0,
        stop=n - 1,
        step=1,
        value=get_idx(),
        on_change=lambda v: set_idx(clamp_index(v if v is not None else 0)),
        label="Keyframe index",
        include_input=True,
    )
    return


@app.cell
def _(mo):
    # Cell 6: prev/next buttons (use run_button)
    prev_btn = mo.ui.run_button(label="Prev")
    next_btn = mo.ui.run_button(label="Next")
    return next_btn, prev_btn


@app.cell
def _(clamp_index, get_jump, mo, n, set_jump):
    # Cell 8 (UI): jump number input (separate from slider)

    jump = mo.ui.number(
        start=0,
        stop=n - 1,
        step=1,
        value=get_jump(),
        on_change=lambda v: set_jump(clamp_index(v if v is not None else 0)),
        label="Jump to index",
    )
    return (jump,)


@app.cell
def _(mo):
    # Cell 9 (UI): go button

    go_btn = mo.ui.run_button(label="Go")
    return (go_btn,)


@app.cell
def _(
    clamp_index,
    get_idx,
    get_jump,
    go_btn,
    next_btn,
    prev_btn,
    set_idx,
    set_jump,
):
    # Cell 10: actions (update state; no UIElement mutation)

    if prev_btn.value:
        set_idx(lambda cur: clamp_index(cur - 1))
        set_jump(get_idx())

    if next_btn.value:
        set_idx(lambda cur: clamp_index(cur + 1))
        set_jump(get_idx())

    if go_btn.value:
        target = clamp_index(get_jump())
        set_idx(target)
    return


@app.cell
def _(
    CACHE_DIR,
    REPORT_JSON,
    VIDEO_PATH,
    clamp_index,
    extract_frame_at_ts,
    get_idx,
    go_btn,
    jump,
    load_timestamps,
    mo,
    next_btn,
    prev_btn,
    set_idx,
):
    # Cell 11: render (vertical stack: current then next)

    def view(VIDEO_PATH, CACHE_DIR, REPORT_JSON):
        timestamps = load_timestamps(REPORT_JSON)
        n = len(timestamps)
        slider = mo.ui.slider(
        start=0,
        stop=n - 1,
        step=1,
        value=get_idx(),
        on_change=lambda v: set_idx(clamp_index(v if v is not None else 0)),
        label="Keyframe index",
        include_input=True,
        )

        i = clamp_index(get_idx())
        j = clamp_index(i + 1)  # next (clamped)

        t1 = timestamps[i]
        t2 = timestamps[j]

        img1 = CACHE_DIR / f"kf_{i:06d}_{t1:.3f}s.jpg"
        img2 = CACHE_DIR / f"kf_{j:06d}_{t2:.3f}s.jpg"

        extract_frame_at_ts(VIDEO_PATH, t1, img1)
        extract_frame_at_ts(VIDEO_PATH, t2, img2)

        controls = mo.hstack([prev_btn, next_btn, slider, jump, go_btn])

        frames = mo.vstack(
            [
                mo.vstack([mo.md(f"**Previous**  \nidx={i}  \nt={t1:.3f}s"), mo.image(str(img1))]),
                mo.vstack([mo.md(f"**Current**  \nidx={j}  \nt={t2:.3f}s"), mo.image(str(img2))]),
            ]
        )

        return mo.vstack([controls, frames])

    view(VIDEO_PATH, CACHE_DIR, REPORT_JSON)
    return (view,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## resizing to a area
    """)
    return


@app.cell
def _(Image, mo, np, source_frame):
    # import numpy as np
    # from PIL import Image
    import plotly.graph_objects as go
    # import marimo as mo

    ROI_DEFAULT = dict(x=0, y=0, w=600, h=900)
    SCALE_DEFAULT = 2

    get_x, set_x = mo.state(int(ROI_DEFAULT["x"]))
    get_y, set_y = mo.state(int(ROI_DEFAULT["y"]))
    get_w, set_w = mo.state(int(ROI_DEFAULT["w"]))
    get_h, set_h = mo.state(int(ROI_DEFAULT["h"]))
    get_scale, set_scale = mo.state(int(SCALE_DEFAULT))

    def set_roi(x: int, y: int, w: int, h: int) -> None:
        set_x(max(0, int(x)))
        set_y(max(0, int(y)))
        set_w(max(1, int(w)))
        set_h(max(1, int(h)))

    # Use one frame as the reference for picking ROI (e.g., current keyframe)
    # Assumes you already extracted img1 somewhere (Path) like in your previous code.
    REFERENCE_FRAME = source_frame

    # Your existing ROI state setters from earlier snippet:
    # get_x,set_x / get_y,set_y / get_w,set_w / get_h,set_h

    pick_btn = mo.ui.run_button(label="Set ROI from selection")

    # Optional: grid density for selectable points (smaller -> more points -> slower)
    GRID_STEP = 8  # pixels

    def _make_roi_picker(frame_path: str):
        im = Image.open(frame_path).convert("RGB")
        W, H = im.size

        # Build a grid of selectable points across the image
        xs = np.arange(0, W, GRID_STEP, dtype=float)
        ys = np.arange(0, H, GRID_STEP, dtype=float)
        X, Y = np.meshgrid(xs, ys)
        x = X.ravel()
        y = Y.ravel()

        fig = go.Figure()

        # Invisible-ish points used for selection
        fig.add_trace(
            go.Scattergl(
                x=x,
                y=y,
                mode="markers",
                marker=dict(size=3, opacity=0.02),
                hoverinfo="skip",
            )
        )

        # Put the image behind the points; keep axes in pixel coordinates
        fig.add_layout_image(
            dict(
                source=im,
                x=0,
                y=0,
                xref="x",
                yref="y",
                sizex=W,
                sizey=H,
                sizing="stretch",
                layer="below",
            )
        )

        fig.update_xaxes(range=[0, W], visible=False)
        fig.update_yaxes(range=[0, H], autorange="reversed", visible=False, scaleanchor="x")
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            dragmode="select",
            height=min(900, H),
        )

        plot = mo.ui.plotly(
            fig,
            config={
                "displaylogo": False,
                "modeBarButtonsToAdd": ["select2d", "lasso2d"],
            },
            label="Drag a box to select ROI",
        )
        return plot, (W, H)

    roi_plot, (FRAME_W, FRAME_H) = _make_roi_picker(str(REFERENCE_FRAME))
    return (
        get_h,
        get_scale,
        get_w,
        get_x,
        get_y,
        pick_btn,
        roi_plot,
        set_h,
        set_w,
        set_x,
        set_y,
    )


@app.cell
def _(mo, pick_btn, roi_plot, set_h, set_w, set_x, set_y):
    def _ranges_to_roi(ranges: dict) -> tuple[int, int, int, int] | None:
        # marimo exposes Plotly range selections via plot.ranges :contentReference[oaicite:2]{index=2}
        xr = ranges.get("x")
        yr = ranges.get("y")
        if not xr or not yr or len(xr) != 2 or len(yr) != 2:
            return None

        x0, x1 = sorted([int(round(xr[0])), int(round(xr[1]))])
        y0, y1 = sorted([int(round(yr[0])), int(round(yr[1]))])

        w = max(1, x1 - x0)
        h = max(1, y1 - y0)
        return x0, y0, w, h

    sel = _ranges_to_roi(roi_plot.ranges)

    roi_status = (
        mo.md("Drag a rectangle selection on the image.")
        if sel is None
        else mo.md(f"Selection: x={sel[0]}, y={sel[1]}, w={sel[2]}, h={sel[3]}")
    )

    if pick_btn.value and sel is not None:
        x0, y0, w, h = sel
        set_x(x0); set_y(y0); set_w(w); set_h(h)

    mo.vstack([roi_plot, mo.hstack([pick_btn, roi_status])])
    return (sel,)


@app.cell
def _(sel):
    sel
    return


@app.cell
def _(Optional, Path, dataclass, subprocess):
    from dataclasses import field, fields as dc_fields
    from typing import List, Iterable, Dict

    def _desc(s: str) -> dict:
        return {"desc": s}

    @dataclass
    class Preset:
        """
        A named encoding recipe expressed in ffmpeg-option terms.

        This models a common subset of ffmpeg flags and adds "extra args" escape hatches
        so you can pass arbitrary ffmpeg options without changing the schema.
        """

        # Identity
        name: str = field(metadata=_desc("Preset identifier used on CLI and appended to output filename."))
        description: str = field(metadata=_desc("Human-readable summary of what the preset optimizes for."))

        # Output
        container: str = field(metadata=_desc("Output container/extension (e.g. 'webm', 'mp4')."))

        # Runner mode
        mode: str = field(metadata=_desc("Execution mode: 'onepass', 'av1_2pass_size', or 'av1_2pass_bitrate'."))

        # Stream selection (-map)
        map_v: str = field(default="0:v:0", metadata=_desc("Video stream selector for -map (default first video)."))
        map_a: str = field(default="0:a:0?", metadata=_desc("Audio stream selector for -map (default first audio, optional)."))

        # Video options (ffmpeg-style)
        c_v: str = field(default="libx264", metadata=_desc("Video encoder for -c:v (e.g. libx264, libsvtav1)."))
        preset: Optional[str] = field(default=None, metadata=_desc("Encoder -preset (x264: 'slow'; SVT-AV1: number)."))
        crf: Optional[int] = field(default=None, metadata=_desc("CRF quality target for -crf (lower=better, bigger)."))
        b_v: Optional[str] = field(default=None, metadata=_desc("Video bitrate for -b:v (e.g. '2000k', '0')."))
        maxrate: Optional[str] = field(default=None, metadata=_desc("VBV cap -maxrate (e.g. '2M')."))
        bufsize: Optional[str] = field(default=None, metadata=_desc("VBV buffer -bufsize (e.g. '2M')."))
        pix_fmt: str = field(default="yuv420p", metadata=_desc("Pixel format for -pix_fmt (e.g. yuv420p)."))

        # Audio options (ffmpeg-style)
        c_a: str = field(default="copy", metadata=_desc("Audio codec for -c:a ('copy' to passthrough)."))
        b_a: Optional[str] = field(default=None, metadata=_desc("Audio bitrate for -b:a when encoding (e.g. '96k')."))

        # Size targeting (only for av1_2pass_size)
        target_mib: Optional[float] = field(
            default=None,
            metadata=_desc("Total target size in MiB (headroom). Used only in 'av1_2pass_size'."),
        )

        # Extra args escape hatches (strings are shlex-split)
        extra_global: List[str] = field(
            default_factory=list,
            metadata=_desc("Extra args inserted after 'ffmpeg -y' (apply to whole command)."),
        )
        extra_input_pre: List[str] = field(
            default_factory=list,
            metadata=_desc("Extra args inserted BEFORE '-i <input>' (demuxer/input options)."),
        )
        extra_video: List[str] = field(
            default_factory=list,
            metadata=_desc("Extra args inserted after video options (apply to video stream)."),
        )
        extra_audio: List[str] = field(
            default_factory=list,
            metadata=_desc("Extra args inserted after audio options (apply to audio stream)."),
        )
        extra_output: List[str] = field(
            default_factory=list,
            metadata=_desc("Extra args inserted before output filename (container/mux/metadata flags)."),
        )

    PRESETS: Dict[str, Preset] = {
        "ffshare": Preset(
            name="ffshare",
            description="Default share compression (matches the one-liner).",
            container="mp4",
            mode="onepass",
            c_v="libx264",
            preset=None,
            crf=23,
            maxrate="2M",
            bufsize="2M",
            pix_fmt="yuv420p",
            c_a="aac",
            b_a=None,
            extra_video=["-vf", "format=yuv420p"],
        ),
        "ffshare_video_only": Preset(
            name="ffshare_video_only",
            description="ffshare default but without audio.",
            container="mp4",
            mode="onepass",
            map_v="0:v:0",
            map_a="0:a:0?",
            c_v="libx264",
            preset="slow",
            crf=23,
            maxrate="2M",
            bufsize="2M",
            pix_fmt="yuv420p",
            c_a="copy",
            extra_global=["-an"],
            extra_video=["-vf", "format=yuv420p"],
        ),
        "ffshare_mkv_video_only": Preset(
            name="ffshare_video_only",
            description="ffshare default but without audio.",
            container="mp4",
            mode="onepass",
            map_v="0:v:0",
            map_a="0:a:0?",
            c_v="libx264",
            preset="slow",
            crf=23,
            maxrate="2M",
            bufsize="2M",
            pix_fmt="yuv420p",
            c_a="copy",
            extra_global=["-an"],
            extra_video=["-vf", "format=yuv420p"],
        ),
        "ffshare_audio_compressed": Preset(
            name="ffshare_audio_compressed",
            description="ffshare video settings + explicit AAC audio bitrate (smaller).",
            container="mp4",
            mode="onepass",
            c_v="libx264",
            preset=None,
            crf=23,
            maxrate="2M",
            bufsize="2M",
            pix_fmt="yuv420p",
            c_a="aac",
            b_a="128k",
            extra_video=["-vf", "format=yuv420p"],
        ),
        "av1_15mb_audio": Preset(
            name="av1_15mb_audio",
            description=(
                "Makes a smaller WebM video that stays under ~15 MB while keeping it looking and sounding decent. "
                "faces are blurry, text is a still legible, but a little blurry"
            ),
            container="webm",
            mode="av1_2pass_size",
            c_v="libsvtav1",
            preset="8",
            pix_fmt="yuv420p",
            c_a="libopus",
            b_a="64k",
            target_mib=14.7,
        ),
        "av1_2pass_1200k_opus64": Preset(
            name="av1_2pass_1200k_opus64",
            description=(
                "Two-pass AV1 (SVT-AV1 preset 8) at fixed 1200k video + Opus 64k. "
                "Middle ground: typically better than size-targeted ~15MB AV1, smaller than ffshare."
            ),
            container="webm",
            mode="av1_2pass_bitrate",
            map_v="0:v:0",
            map_a="0:a:0?",
            c_v="libsvtav1",
            preset="8",
            b_v="1200k",
            pix_fmt="yuv420p",
            c_a="libopus",
            b_a="64k",
        ),
        "av1_crf28_opus128": Preset(
            name="av1_crf28_opus128",
            description="One-pass AV1 CRF encode with Opus 128k (general small+quality).",
            container="webm",
            mode="onepass",
            c_v="libsvtav1",
            preset="6",
            crf=28,
            b_v="0",
            pix_fmt="yuv420p",
            c_a="libopus",
            b_a="128k",
        ),
        "crop_no_audio": Preset(
            name="crop_no_audio",
            description="Crop video using ROI and remove audio (-an). Keeps default video settings from your pipeline.",
            container="mkv",
            mode="onepass",
            map_v="0:v:0",
            map_a="0:a:0?",          # irrelevant when -an is present, but fine
            c_v="libx264",
            preset=None,
            crf=None,
            b_v=None,
            maxrate=None,
            bufsize=None,
            pix_fmt="yuv420p",
            c_a="copy",
            b_a=None,
            extra_global=["-an"],    # removes audio
            extra_video=[],          # crop is injected by crop_video_with_preset(...)
            extra_audio=[],
            extra_output=[],
        ),
    }


    def crop_video_with_preset(
        in_path: Path,
        preset: Preset | None = None,   # NEW: optional
        *,
        x: int,
        y: int,
        w: int,
        h: int,
        out_dir: Path | None = None,
        out_path: Path | None = None,
        tag: str | None = None,
        scale: int | None = None,
        start: float | None = None,
        duration: float | None = None,
        align_to_even: bool = True,
        overwrite: bool = True,
        dry_run: bool = False,
    ) -> tuple[Path, list[str]] | Path:
        """
        If preset is None: apply crop (+ optional scale/trim), keep audio copy, and use a safe default video encode.
        If preset is provided: apply crop merged with preset filters and preset options (onepass only).
        """

        def _safe(s: str) -> str:
            return "".join(ch if (ch.isalnum() or ch in ("-", "_", ".")) else "_" for ch in s)

        def _even(v: int) -> int:
            v = int(v)
            return v if v % 2 == 0 else max(2, v - 1)

        x = max(0, int(x))
        y = max(0, int(y))
        w = max(1, int(w))
        h = max(1, int(h))

        # Pick defaults when no preset is selected
        default_container = (in_path.suffix.lstrip(".") or "mp4")
        default_c_v = "libx264"
        default_pix_fmt = "yuv420p"

        pix_fmt = (preset.pix_fmt if preset else default_pix_fmt) or default_pix_fmt
        if align_to_even and pix_fmt.lower() == "yuv420p":
            w = _even(w)
            h = _even(h)

        # --- Build filtergraph: crop (+ optional scale) + (preset vf if any)
        def _vf_crop() -> str:
            parts = [f"crop={w}:{h}:{x}:{y}"]
            if scale and int(scale) > 1:
                s = int(scale)
                parts.append(f"scale=iw*{s}:ih*{s}")
            return ",".join(parts)

        vf_parts = [_vf_crop()]
        stripped_extra_video: list[str] = []

        if preset:
            if preset.mode != "onepass":
                raise ValueError(f"crop_video_with_preset only implements mode='onepass' (got {preset.mode!r}).")

            extra_video = list(preset.extra_video or [])
            i = 0
            while i < len(extra_video):
                tok = extra_video[i]
                if tok in ("-vf", "-filter:v"):
                    if i + 1 >= len(extra_video):
                        raise ValueError(f"{tok} present in preset.extra_video but missing filtergraph value")
                    vf_parts.append(str(extra_video[i + 1]))
                    i += 2
                    continue
                stripped_extra_video.append(tok)
                i += 1

        vf = ",".join([p for p in vf_parts if p])

        # --- Output dir + path (same folder as input, tagged)
        def _default_tag() -> str:
            parts = []
            if preset:
                parts.append(preset.name)
            parts.append(f"crop_{x}x{y}_{w}x{h}")
            if scale and int(scale) > 1:
                parts.append(f"s{int(scale)}")
            if start is not None:
                parts.append(f"ss{float(start):.3f}")
            if duration is not None:
                parts.append(f"t{float(duration):.3f}")
            return _safe("__".join(parts))

        container = preset.container if preset else default_container

        if out_path is None:
            if out_dir is None:
                tag_final = tag or _default_tag()
                out_dir = in_path.parent / _safe(f"{in_path.stem}__{tag_final}")
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / _safe(f"{in_path.stem}.{container}")

        # --- Audio disabled?
        extra_global = list(preset.extra_global or []) if preset else []
        audio_disabled = any(a == "-an" for a in extra_global)

        # --- Assemble ffmpeg command
        cmd: list[str] = ["ffmpeg"]
        if overwrite:
            cmd += ["-y"]
        cmd += extra_global

        if start is not None:
            cmd += ["-ss", f"{float(start):.6f}"]
        if duration is not None:
            cmd += ["-t", f"{float(duration):.6f}"]

        cmd += (list(preset.extra_input_pre or []) if preset else [])
        cmd += ["-i", str(in_path)]

        # Mapping
        if preset:
            cmd += ["-map", preset.map_v]
            if not audio_disabled and preset.map_a:
                cmd += ["-map", preset.map_a]
        else:
            cmd += ["-map", "0:v:0"]
            if not audio_disabled:
                cmd += ["-map", "0:a:0?"]

        # Video options
        if preset:
            cmd += ["-c:v", preset.c_v]
            if preset.preset:
                cmd += ["-preset", str(preset.preset)]
            if preset.crf is not None:
                cmd += ["-crf", str(int(preset.crf))]
            if preset.b_v:
                cmd += ["-b:v", str(preset.b_v)]
            if preset.maxrate:
                cmd += ["-maxrate", str(preset.maxrate)]
            if preset.bufsize:
                cmd += ["-bufsize", str(preset.bufsize)]
            cmd += ["-pix_fmt", str(preset.pix_fmt or pix_fmt)]
        else:
            # "crop only": no preset tuning; still must re-encode video to apply the crop filter
            cmd += ["-c:v", default_c_v, "-pix_fmt", pix_fmt]

        # Filters
        if vf:
            cmd += ["-vf", vf]

        # Extra video args (minus any -vf we merged)
        if preset:
            cmd += stripped_extra_video

        # Audio options
        if not audio_disabled:
            if preset:
                cmd += ["-c:a", preset.c_a]
                if preset.b_a and preset.c_a != "copy":
                    cmd += ["-b:a", str(preset.b_a)]
                cmd += list(preset.extra_audio or [])
            else:
                cmd += ["-c:a", "copy"]

        # Output extras + filename
        if preset:
            cmd += list(preset.extra_output or [])
        cmd += [str(out_path)]

        if dry_run:
            return out_path, cmd

        out_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(cmd, check=True)
        return out_path
    return List, PRESETS, crop_video_with_preset


@app.cell
def _(
    PRESETS: "Dict[str, Preset]",
    ai_invasion_1,
    crop_video_with_preset,
    get_h,
    get_scale,
    get_w,
    get_x,
    get_y,
):
    out = crop_video_with_preset(
        ai_invasion_1,
        PRESETS["crop_no_audio"],
        x=get_x(), y=get_y(), w=get_w(), h=get_h(),
        scale=get_scale(),
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## reviewing cropped keyframes
    """)
    return


@app.cell
def _(video_dir):
    ai_invasion_1_cropped = video_dir / "Doug_and_Twitch_Chat_TAKE_OVER_EUROPE-VpmmuHlLPM0__crop_no_audio__crop_0x14_350x460__s2" / "cropped_Doug_and_Twitch_Chat_TAKE_OVER_EUROPE-VpmmuHlLPM0.mkv"
    ai_invasion_1_cropped
    return (ai_invasion_1_cropped,)


@app.cell
def _(ai_invasion_1_cropped, data_dir, keyframe_report):
    cropped_report = keyframe_report(ai_invasion_1_cropped , data_dir)
    return (cropped_report,)


@app.cell
def _(cropped_report):
    cropped_report
    return


@app.cell
def _(cropped_report):
    cropped_report.output
    return


@app.cell
def _(cropped_report, json):
    with open(cropped_report.output, "r", encoding="utf-8") as _f:
        cropped_report_dict = json.load(_f)
    return (cropped_report_dict,)


@app.cell
def _(cropped_report_dict):
    cropped_report_dict
    return


@app.cell
def _(ai_invasion_1_cropped, supporting_files, view):
    # ---------- config ----------
    # VIDEO_PATH = ai_invasion_1
    CROPPED_REPORT_JSON =  supporting_files / "data" / "cropped_Doug_and_Twitch_Chat_TAKE_OVER_EUROPE-VpmmuHlLPM0_keyframes_report.json" 
    CROPPED_CACHE_DIR = supporting_files / "data" / "cropped_keyframe_cache"

    view(VIDEO_PATH=ai_invasion_1_cropped,CACHE_DIR=CROPPED_CACHE_DIR, REPORT_JSON=CROPPED_REPORT_JSON)
    return


@app.cell
def _():
    return


@app.cell(column=5, hide_code=True)
def _(mo):
    mo.md(r"""
    # chagpt suggested frame extraction
    """)
    return


@app.cell
def _(Path):
    from __future__ import annotations

    from dataclasses import dataclass, asdict
    import json
    import subprocess
    from typing import Iterable, Optional

    import numpy as np
    from PIL import Image


    @dataclass(frozen=True)
    class KeptFrame:
        """
        Metadata for a kept frame.

        Fields:
          - index: 0-based index in the decoded candidate stream (after optional fps sampling).
          - t_sec: approximate timestamp in seconds for this decoded frame.
          - dy_px: estimated vertical scroll (pixels) since the last kept frame.
          - corr: alignment correlation score (higher is better).
          - bottom_change: mean absolute difference in the bottom band vs last kept frame.
          - saved_path: path to a saved PNG (if saving enabled), else None.
        """
        index: int
        t_sec: float
        dy_px: int
        corr: float
        bottom_change: float
        saved_path: Optional[str]


    def _ffprobe_video_info(video: Path) -> tuple[int, int, float]:
        """
        Returns (width, height, fps_estimate).

        fps_estimate is derived from avg_frame_rate when available.
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height,avg_frame_rate,r_frame_rate",
            "-of", "json",
            str(video),
        ]
        out = subprocess.check_output(cmd)
        info = json.loads(out.decode("utf-8"))
        stream = info["streams"][0]
        w = int(stream["width"])
        h = int(stream["height"])

        def parse_rate(s: str) -> float:
            # e.g. "30000/1001"
            if not s or s == "0/0":
                return 0.0
            num, den = s.split("/")
            num_f = float(num)
            den_f = float(den) if float(den) != 0 else 1.0
            return num_f / den_f

        fps = parse_rate(stream.get("avg_frame_rate", "")) or parse_rate(stream.get("r_frame_rate", "")) or 0.0
        if fps <= 0:
            fps = 1.0
        return w, h, fps


    def _row_energy(gray_u8: np.ndarray, downsample: int = 2) -> np.ndarray:
        """
        Computes a normalized 1D "edge energy per row" vector used for vertical alignment.
        """
        a = gray_u8[::downsample, ::downsample].astype(np.float32) / 255.0

        # Cheap gradient magnitude proxy
        dx = np.abs(a[:, 1:] - a[:, :-1])              # (H, W-1)
        dy = np.abs(a[1:, :] - a[:-1, :])              # (H-1, W)
        row_dx = dx.mean(axis=1)                       # (H,)
        row_dy = dy.mean(axis=1)                       # (H-1,)
        row_dy = np.concatenate([row_dy, row_dy[-1:]]) # pad to (H,)

        row = row_dx + row_dy
        row = (row - row.mean()) / (row.std() + 1e-6)
        return row


    def _estimate_dy(row_a: np.ndarray, row_b: np.ndarray, max_shift: int) -> tuple[int, float]:
        """
        Estimates vertical shift dy that best aligns row_a to row_b using correlation.
        Returns (dy, corr). Higher corr is better.
        """
        best_s = 0
        best_corr = -1e9
        n = len(row_a)

        for s in range(-max_shift, max_shift + 1):
            if s >= 0:
                x = row_a[s:]
                y = row_b[: len(x)]
            else:
                x = row_a[: n + s]
                y = row_b[-s:]
            if len(x) < 80:
                continue
            corr = float((x * y).mean())
            if corr > best_corr:
                best_corr = corr
                best_s = s
        return best_s, best_corr


    def _estimate_line_height(row: np.ndarray) -> int:
        """
        Roughly estimates line spacing in pixels (in the *downsampled* row domain).
        Returns a median peak spacing; falls back if peak detection is weak.
        """
        thr = float(np.quantile(row, 0.85))
        peaks: list[int] = []
        for i in range(2, len(row) - 2):
            if row[i] > thr and row[i] > row[i - 1] and row[i] > row[i + 1]:
                peaks.append(i)

        if len(peaks) < 6:
            return 18  # downsampled fallback (~36 px if downsample=2)

        d = np.diff(peaks)
        d = d[(d >= 9) & (d <= 35)]  # downsampled plausible range
        if len(d) == 0:
            return 18
        return int(np.median(d))


    def _bottom_change(a_u8: np.ndarray, b_u8: np.ndarray, band_h: int, downsample: int = 2) -> float:
        """
        Mean absolute difference on the bottom band (after downsampling).
        """
        a = a_u8[::downsample, ::downsample].astype(np.float32) / 255.0
        b = b_u8[::downsample, ::downsample].astype(np.float32) / 255.0
        bh = max(1, band_h // downsample)
        aa = a[-bh:, :]
        bb = b[-bh:, :]
        return float(np.mean(np.abs(aa - bb)))


    def _iter_gray_frames_ffmpeg(
        video: Path,
        width: int,
        height: int,
        *,
        sample_fps: Optional[float] = None,
    ) -> Iterable[np.ndarray]:
        """
        Yields grayscale frames as uint8 arrays (H, W) from ffmpeg.
        If sample_fps is provided, frames are sampled at that rate.
        """
        vf = "format=gray"
        if sample_fps is not None:
            vf = f"fps={sample_fps},{vf}"

        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel", "error",
            "-vsync", "0",
            "-i", str(video),
            "-an",
            "-vf", vf,
            "-f", "rawvideo",
            "-pix_fmt", "gray",
            "pipe:1",
        ]

        frame_size = width * height
        with subprocess.Popen(cmd, stdout=subprocess.PIPE) as proc:
            assert proc.stdout is not None
            while True:
                buf = proc.stdout.read(frame_size)
                if not buf or len(buf) < frame_size:
                    break
                frame = np.frombuffer(buf, dtype=np.uint8).reshape((height, width))
                yield frame
            proc.wait()


    def reduce_chat_frames_by_scroll(
        video_path: Path | str,
        out_dir: Path | str,
        *,
        sample_fps: Optional[float] = None,
        lines_per_keep: int = 8,
        min_corr: float = 0.75,
        max_shift_px: int = 220,
        bottom_band_h_px: int = 160,
        bottom_change_thr: float = 0.05,
        downsample: int = 2,
        save_png: bool = True,
        write_report_json: bool = True,
    ) -> list[KeptFrame]:
        """
        Reduces a chat-overlay video to a smaller set of representative frames using scroll-distance gating.

        Strategy:
          - Estimate vertical scroll dy between frames without OCR (row-energy correlation).
          - Accumulate scroll since last kept frame.
          - Keep a frame when:
              (accum_scroll >= lines_per_keep * line_height) OR
              (bottom band changed enough to indicate new content/emote-only lines)

        Args:
          video_path: path to the cropped chat video.
          out_dir: directory to write selected PNGs and a JSON report.
          sample_fps: if set, decode frames at this FPS (recommended if input is high-FPS).
                      if None, uses the video’s native decode rate.
          lines_per_keep: how many chat lines worth of scroll to allow before keeping a new frame.
          min_corr: minimum alignment correlation for accepting a dy estimate.
          max_shift_px: maximum vertical shift to search (pixels at full resolution).
          bottom_band_h_px: height (pixels) of the bottom band used for change detection.
          bottom_change_thr: threshold for bottom band change to force a keep.
          downsample: internal downsampling factor for alignment/change computation.
          save_png: if True, saves kept frames as PNG files.
          write_report_json: if True, writes a report.json containing kept frame metadata.

        Returns:
          List of KeptFrame entries in chronological order.
        """
        video = Path(video_path)
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)

        w, h, fps_native = _ffprobe_video_info(video)
        fps_used = float(sample_fps) if sample_fps is not None else float(fps_native)

        kept: list[KeptFrame] = []

        last_kept_frame: Optional[np.ndarray] = None
        last_kept_row: Optional[np.ndarray] = None
        accum_scroll = 0.0
        line_h_ds: Optional[int] = None  # line height in downsampled-row units

        # Convert max_shift into downsampled units for speed
        max_shift_ds = max(10, int(max_shift_px / downsample))

        for i, frame_u8 in enumerate(_iter_gray_frames_ffmpeg(video, w, h, sample_fps=sample_fps)):
            t_sec = i / fps_used

            row = _row_energy(frame_u8, downsample=downsample)

            if last_kept_frame is None:
                # Estimate line height once from the first kept frame
                line_h_ds = _estimate_line_height(row)
                save_path = None
                if save_png:
                    save_path = str(out / f"frame_{i:06d}_t{t_sec:010.3f}.png")
                    Image.fromarray(frame_u8, mode="L").save(save_path)
                entry = KeptFrame(
                    index=i,
                    t_sec=float(t_sec),
                    dy_px=0,
                    corr=1.0,
                    bottom_change=0.0,
                    saved_path=save_path,
                )
                kept.append(entry)
                last_kept_frame = frame_u8
                last_kept_row = row
                accum_scroll = 0.0
                continue

            assert last_kept_row is not None and last_kept_frame is not None and line_h_ds is not None

            dy_ds, corr = _estimate_dy(last_kept_row, row, max_shift=max_shift_ds)
            if corr < min_corr:
                continue

            accum_scroll += abs(dy_ds)

            bc = _bottom_change(last_kept_frame, frame_u8, band_h=bottom_band_h_px, downsample=downsample)

            keep_now = (accum_scroll >= lines_per_keep * line_h_ds) or (bc >= bottom_change_thr)

            if keep_now:
                save_path = None
                if save_png:
                    save_path = str(out / f"frame_{i:06d}_t{t_sec:010.3f}.png")
                    Image.fromarray(frame_u8, mode="L").save(save_path)

                entry = KeptFrame(
                    index=i,
                    t_sec=float(t_sec),
                    dy_px=int(dy_ds * downsample),
                    corr=float(corr),
                    bottom_change=float(bc),
                    saved_path=save_path,
                )
                kept.append(entry)
                last_kept_frame = frame_u8
                last_kept_row = row
                accum_scroll = 0.0

        if write_report_json:
            report_path = out / "report.json"
            report = {
                "video": str(video),
                "sample_fps": sample_fps,
                "fps_used_for_timestamps": fps_used,
                "lines_per_keep": lines_per_keep,
                "min_corr": min_corr,
                "max_shift_px": max_shift_px,
                "bottom_band_h_px": bottom_band_h_px,
                "bottom_change_thr": bottom_change_thr,
                "downsample": downsample,
                "kept_count": len(kept),
                "kept": [asdict(k) for k in kept],
            }
            report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

        return kept


    # Example:
    # out_dir = ai_invasion_1_cropped.parent / "_selected_frames_scroll"
    # kept = reduce_chat_frames_by_scroll(
    #     ai_invasion_1_cropped,
    #     out_dir,
    #     sample_fps=None,      # set e.g. 1.0 or 2.0 if your input is high-FPS
    #     lines_per_keep=8,     # increase to reduce more (e.g., 10–12)
    # )
    # print(len(kept), "frames kept")

    return (
        Image,
        Optional,
        asdict,
        dataclass,
        json,
        np,
        reduce_chat_frames_by_scroll,
        subprocess,
    )


@app.cell
def _(ai_invasion_1_cropped, data_dir, reduce_chat_frames_by_scroll):
    out_dir = data_dir / "chat_frames"
    kept = reduce_chat_frames_by_scroll(ai_invasion_1_cropped, out_dir, lines_per_keep=8)

    return


@app.cell
def _():
    return


@app.cell(column=6, hide_code=True)
def _(mo):
    mo.md(r"""
    # batch processing tests
    I wanted to see how well a vlm can process a batch of overlapping chat messages
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
