"""Typed models for transcription results and metadata."""

from pydantic import BaseModel, Field


class WordTimestamp(BaseModel):
    """Word-level timestamp produced by transcription alignment."""

    word: str = Field(description="Recognized word token.")
    start: float = Field(description="Word start time in seconds.")
    end: float = Field(description="Word end time in seconds.")
    probability: float | None = Field(
        default=None,
        description="Optional confidence/probability for the word token.",
    )


class TranscriptSegment(BaseModel):
    """Segment-level transcript chunk containing aligned words."""

    id: int = Field(description="Segment identifier from the ASR output.")
    start: float = Field(description="Segment start time in seconds.")
    end: float = Field(description="Segment end time in seconds.")
    text: str = Field(description="Segment text content.")
    words: list[WordTimestamp] = Field(
        default_factory=list,
        description="Word-level timestamps contained in this segment.",
    )
    avg_logprob: float | None = Field(
        default=None,
        description="Average log probability for the segment, when provided.",
    )


class TranscriptResult(BaseModel):
    """Complete transcript result for a single VOD audio source."""

    segments: list[TranscriptSegment] = Field(
        default_factory=list,
        description="Ordered transcript segments with optional word-level detail.",
    )
    language: str = Field(description="Detected language code for the transcript.")
    language_probability: float = Field(
        description="Probability/confidence for the detected language."
    )
    audio_path: str = Field(description="Path to the source audio file.")


class TranscriptMetadata(BaseModel):
    """Metadata sidecar schema for transcript artifacts."""

    source_file: str = Field(description="Original source audio file path.")
    language: str = Field(description="Detected transcript language code.")
    model: str = Field(description="Whisper model identifier used for transcription.")
    align_model: str = Field(
        description="Alignment model identifier used for word-level timestamps."
    )
    word_count: int = Field(description="Total number of transcribed words.")
    duration_seconds: float = Field(
        description="Transcript duration in seconds based on segment timing."
    )
    compute_type: str = Field(
        description="Model compute precision or quantization mode."
    )
    batch_size: int = Field(description="Batch size used during transcription.")
