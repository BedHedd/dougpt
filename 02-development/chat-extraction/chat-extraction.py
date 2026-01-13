import marimo

__generated_with = "0.18.4"
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
def _(Path, video_dir):
    files = [file.name for file in Path(video_dir).iterdir()]
    files
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
    frame = supporting_files / "data" / "frame.png"
    frame
    return (frame,)


@app.cell
def _(frame, p):
    import subprocess, shlex

    cmd = f'ffmpeg -v error -ss 5.2 -i {'"' + str(p) + '"'} -frames:v 1 -update 1 {frame}'
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
    # sh("ffprobe", "-hide_banner", "-select_streams", "v:0", "-show_entries", "stream=codec_name,pix_fmt,width,height,avg_frame_rate", "-of", "default=nw=1", VIDEO)

    # # ffmpeg software decode test (first frame)
    # sh("ffmpeg", "-hide_banner", "-v", "error", "-i", VIDEO, "-frames:v", "1", "-f", "null", "-")

    # # VAAPI capability check via vainfo (uses nix shell if vainfo not installed)
    # if sh("bash", "-lc", "command -v vainfo >/dev/null") != 0:
    #     sh("nix", "shell", "nixpkgs#libva-utils", "-c", "vainfo")
    # else:
    #     sh("vainfo")

    # # ffmpeg VAAPI decode test (first frame)
    # sh("bash", "-lc", f"ls -l /dev/dri/renderD* || true")
    # sh("ffmpeg", "-hide_banner", "-v", "error",
    #    "-vaapi_device", "/dev/dri/renderD128",
    #    "-hwaccel", "vaapi", "-hwaccel_output_format", "vaapi",
    #    "-i", VIDEO, "-frames:v", "1", "-f", "null", "-")

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
    #     ok, frame = cap.read()
    #     print("read:", ok, None if frame is None else frame.shape)
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

    # ok, frame_bgr = cap.read()
    # cap.release()

    # if not ok:
    #     raise RuntimeError("Could not read frame")
    return


@app.cell
def _():
    # cv2.imwrite("frame_5.2s.png", frame_bgr)

    # t_sec = 5.2

    # cap = cv2.VideoCapture(video)
    # cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)

    # ok, frame_bgr = cap.read()
    # cap.release()

    # if not ok:
    #     raise RuntimeError("Could not read frame")

    # cv2.imwrite("frame_5.2s.png", frame_bgr)
    return


@app.cell
def _():
    return


@app.cell(column=1)
def _(mo):
    mo.md(r"""
    # test with a vison language model
    """)
    return


@app.cell
def _(frame):
    frame.as_posix()
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
def _(frame, mo):
    mo.image(frame.as_posix())
    return


@app.cell
def _(Markdown, frame):
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

    resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe what you see. If there is text, transcribe it."},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(frame.as_posix())}},
                ],
            }
        ],
        temperature=0.7,
        max_tokens=-1,
    )

    Markdown(resp.choices[0].message.content)
    return client, image_file_to_data_url, resp


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


@app.cell
def _(Markdown, client, frame, image_file_to_data_url):
    _resp = client.chat.completions.create(
        model="qwen/qwen3-vl-8b", 
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Get all the chat messages. Please also include usernames with messages"},
                    {"type": "image_url", "image_url": {"url": image_file_to_data_url(frame.as_posix())}},
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


@app.cell(column=3)
def _(mo):
    mo.md(r"""
    # testing frame extraction
    """)
    return


@app.cell
def _(cv2):
    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Optional, Tuple

    # import cv2
    import numpy as np


    @dataclass(frozen=True)
    class MatchResult:
        timestamp_s: float
        score: float
        y_in_chat_px: int
        x_in_chat_px: int


    def find_chat_template_reaches_top(
        video_path: str,
        template_path: str,
        chat_rect: Tuple[int, int, int, int],  # (x, y, w, h) in video pixels
        *,
        top_px: int = 12,
        sample_fps: float = 10.0,
        match_thr: float = 0.80,
        start_s: float = 0.0,
        end_s: float = 0.0,  # 0 = scan to end
        blur: bool = True,
    ) -> Optional[MatchResult]:
        """
        Finds the first timestamp where the given template (e.g., a specific chat line)
        is detected within the chat crop and its top-left Y position is <= top_px.

        Returns MatchResult if found; otherwise None.
        """
        tmpl = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if tmpl is None or tmpl.size == 0:
            raise ValueError(f"Could not read template: {template_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        video_fps = cap.get(cv2.CAP_PROP_FPS)
        if not video_fps or video_fps <= 0:
            video_fps = 30.0

        # Process every Nth frame to approximate sample_fps
        step = max(1, int(round(video_fps / max(sample_fps, 0.1))))

        x, y, w, h = chat_rect
        if w <= 0 or h <= 0:
            raise ValueError("chat_rect must have positive w and h")

        if start_s > 0:
            cap.set(cv2.CAP_PROP_POS_MSEC, start_s * 1000.0)

        # Pre-blur template once if requested
        if blur:
            tmpl_proc = cv2.GaussianBlur(tmpl, (3, 3), 0)
        else:
            tmpl_proc = tmpl

        frame_idx = 0
        while True:
            t_s = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
            if end_s > 0 and t_s > end_s:
                break

            ok, frame = cap.read()
            if not ok:
                break

            if frame_idx % step != 0:
                frame_idx += 1
                continue
            frame_idx += 1

            chat = frame[y : y + h, x : x + w]
            if chat.size == 0:
                raise ValueError("chat_rect is out of bounds for this video frame size")

            gray = cv2.cvtColor(chat, cv2.COLOR_BGR2GRAY)
            if blur:
                gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # Template matching
            res = cv2.matchTemplate(gray, tmpl_proc, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)  # max_loc = (x, y) in chat crop

            if max_val >= match_thr:
                mx, my = int(max_loc[0]), int(max_loc[1])
                if my <= top_px:
                    return MatchResult(timestamp_s=float(t_s), score=float(max_val), y_in_chat_px=my, x_in_chat_px=mx)

        return None
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
        sample_fps: float = 10.0, # how often to sample frames
        match_thr: float = 0.80,  # NCC threshold
        start_s: float = 0.0,
        end_s: float = 0.0,       # 0 = until end
    ) -> Optional[MatchResult]:
        """
        Streams cropped frames via ffmpeg and finds when `template_path` (a cropped image of the chat line)
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

        # ffmpeg: crop chat area, sample fps, grayscale, output raw frames
        vf = f"crop={w}:{h}:{x}:{y},fps={sample_fps},format=gray"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
        if start_s > 0:
            cmd += ["-ss", str(start_s)]
        cmd += ["-i", video_path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "gray", "-"]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdout is not None

        frame_bytes = w * h
        frame_index = 0

        # Use sliding_window_view for vectorized Y-only search (X fixed by taking width=tw slice)
        sliding_window_view = np.lib.stride_tricks.sliding_window_view

        try:
            while True:
                if end_s > 0:
                    # Approximate timestamp based on sampled frames
                    t_s = start_s + (frame_index / sample_fps)
                    if t_s > end_s:
                        break

                buf = proc.stdout.read(frame_bytes)
                if len(buf) != frame_bytes:
                    break

                frame_index += 1
                frame = np.frombuffer(buf, dtype=np.uint8).reshape((h, w))
                band = frame[:H, :]  # top search band

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
                    # Timestamp is approximate based on fps sampling; good enough for frame extraction
                    ts = start_s + ((frame_index - 1) / sample_fps)
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

    return (find_chat_template_reaches_top_noopencv,)


@app.cell
def _(find_chat_template_reaches_top_noopencv, frame, video_dir):
    res = find_chat_template_reaches_top_noopencv(
        video_path=str(video_dir / "better-video-qualityDoug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.15mb.webm"),
        template_path=frame,
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


if __name__ == "__main__":
    app.run()
