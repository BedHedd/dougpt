import marimo

__generated_with = "0.18.4"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from pathlib import Path
    from dotenv import load_dotenv

    try:
        start = Path(__file__).resolve()
    except NameError:
        start = Path.cwd()

    supporting_files = next(p / "00-supporting-files" for p in start.parents if (p / "00-supporting-files").exists())
    return Path, start


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
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
