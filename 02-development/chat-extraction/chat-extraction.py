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
def _(mo, video_dir):
    p = video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0-av1_15mb_audio.webm"
    # p = video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0.mkv"
    mo.Html(f"""
    <video controls style="max-width: 100%; height: auto;">
      <source src="{p}" type="video/mp4">
    </video>
    """)
    return (p,)


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
def _(video_dir):
    import cv2

    video = str(video_dir / "Doug and Twitch Chat TAKE OVER EUROPE-VpmmuHlLPM0-av1_15mb_audio.webm")
    t_sec = 5.2

    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)

    ok, frame_bgr = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError("Could not read frame")

    return cv2, frame_bgr, video


@app.cell
def _(cv2, video):
    cv2.imwrite("frame_5.2s.png", frame_bgr)

    t_sec = 5.2

    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_POS_MSEC, t_sec * 1000)

    ok, frame_bgr = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError("Could not read frame")

    cv2.imwrite("frame_5.2s.png", frame_bgr)
    return (frame_bgr,)


@app.cell(column=1)
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
    resp.choices[0].message.content
    return


@app.cell
def _():
    return


@app.cell(column=2)
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


if __name__ == "__main__":
    app.run()
