"""
Transcript schema models for ASR pipeline.

Defines data models for raw and normalized transcript segments
with per-word confidence, speaker labels, and quality flags.
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class WordTiming(BaseModel):
    """Per-word timing and confidence data."""

    word: str
    start: float  # seconds
    end: float  # seconds
    confidence: Optional[float] = None  # 0-1, from ASR logprob
    logprob: Optional[float] = None  # Raw log probability from ASR


class RawSegment(BaseModel):
    """Raw transcript segment from ASR output."""

    text: str
    start: float  # seconds
    end: float  # seconds
    words: list[WordTiming] = Field(default_factory=list)
    speaker: Optional[str] = None  # Speaker label from diarization
    language: Optional[str] = None
    language_probability: Optional[float] = None


class NormalizedSegment(BaseModel):
    """Normalized transcript segment with confidence metadata."""

    # Identifiers
    segment_id: str  # Unique ID (e.g., "{source_id}-{start_ms}")
    source_id: str

    # Timing
    start: float  # seconds
    end: float  # seconds
    duration_seconds: float

    # Text
    text_raw: str  # Original ASR output
    text_normalized: str  # Normalized (sentence case, punctuation)

    # Speaker
    speaker: Optional[str] = None

    # Confidence metrics
    confidence: float  # Aggregated segment confidence (0-1)
    confidence_method: str = "mean_word"  # How confidence was computed
    word_count: int = 0
    low_confidence_words: int = 0  # Words below threshold

    # Quality flags
    quality_flags: list[str] = Field(default_factory=list)
    # Possible flags: low_confidence, short_segment, no_speaker, overlap_suspected

    # Per-word data
    words: list[WordTiming] = Field(default_factory=list)

    # Metadata
    sample_rate: int = 16000
    channel_map: str = "mono"

    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TranscriptManifest(BaseModel):
    """Manifest for a complete transcript export."""

    source_id: str
    audio_path: str
    manifest_path: Optional[str] = None  # Reference to audio prep manifest

    # ASR config used
    model: str
    language: Optional[str] = None
    compute_type: str = "float16"
    device: str = "cuda"

    # Statistics
    total_segments: int = 0
    total_duration_seconds: float = 0.0
    total_words: int = 0
    avg_confidence: float = 0.0
    low_confidence_segments: int = 0

    # Quality summary
    quality_summary: dict[str, int] = Field(default_factory=dict)

    # Output files
    raw_output: Optional[str] = None
    normalized_output: Optional[str] = None

    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
