"""
Confidence aggregation utilities for ASR transcripts.

Aggregates per-word confidence scores into segment-level metrics
and flags low-confidence spans.
"""

from typing import Optional
import numpy as np
from loguru import logger

from schemas.transcript import WordTiming, NormalizedSegment


def aggregate_segment_confidence(
    words: list[WordTiming],
    method: str = "mean",
    low_confidence_threshold: float = 0.70,
) -> tuple[float, int, int]:
    """
    Aggregate per-word confidence into segment-level confidence.

    Args:
        words: List of WordTiming objects with confidence scores
        method: Aggregation method: "mean", "min", "geometric_mean"
        low_confidence_threshold: Threshold below which words are flagged

    Returns:
        Tuple of (segment_confidence, low_confidence_word_count, total_words)
    """
    if not words:
        return 0.0, 0, 0

    # Extract confidence scores (default to 0.5 if missing)
    confidences = [w.confidence if w.confidence is not None else 0.5 for w in words]

    if not confidences:
        return 0.5, 0, 0

    # Compute aggregate
    if method == "mean":
        segment_conf = float(np.mean(confidences))
    elif method == "min":
        segment_conf = float(np.min(confidences))
    elif method == "geometric_mean":
        # Geometric mean with small epsilon to handle zeros
        confs = np.array(confidences) + 1e-10
        segment_conf = float(np.exp(np.mean(np.log(confs))))
    else:
        logger.warning(f"Unknown confidence method: {method}, using mean")
        segment_conf = float(np.mean(confidences))

    # Count low-confidence words
    low_count = sum(1 for c in confidences if c < low_confidence_threshold)

    return segment_conf, low_count, len(words)


def flag_low_confidence_segments(
    segments: list[NormalizedSegment],
    threshold: float = 0.70,
    flag_name: str = "low_confidence",
) -> list[NormalizedSegment]:
    """
    Add quality flags to segments with low confidence.

    Args:
        segments: List of NormalizedSegment objects
        threshold: Confidence threshold for flagging
        flag_name: Name of the flag to add

    Returns:
        List of segments with updated quality_flags
    """
    for segment in segments:
        if segment.confidence < threshold and flag_name not in segment.quality_flags:
            segment.quality_flags.append(flag_name)

    return segments


def compute_quality_summary(
    segments: list[NormalizedSegment],
) -> dict[str, int]:
    """
    Compute summary statistics of quality flags.

    Args:
        segments: List of NormalizedSegment objects

    Returns:
        Dict mapping flag names to counts
    """
    summary: dict[str, int] = {}

    for segment in segments:
        for flag in segment.quality_flags:
            summary[flag] = summary.get(flag, 0) + 1

    return summary


def confidence_from_logprob(logprob: float) -> float:
    """
    Convert log probability to confidence score.

    Args:
        logprob: Log probability from ASR model

    Returns:
        Confidence score in [0, 1]
    """
    # Typical logprobs range from -5 to 0
    # Map to [0, 1] where -5 -> 0.0 and 0 -> 1.0
    # Using sigmoid-like transformation
    confidence = 1.0 / (1.0 + np.exp(-logprob))
    return float(confidence)


def compute_segment_statistics(segments: list[NormalizedSegment]) -> dict:
    """
    Compute overall statistics for a transcript.

    Args:
        segments: List of NormalizedSegment objects

    Returns:
        Dict with statistics: total_segments, total_duration, total_words,
                               avg_confidence, low_confidence_count
    """
    if not segments:
        return {
            "total_segments": 0,
            "total_duration_seconds": 0.0,
            "total_words": 0,
            "avg_confidence": 0.0,
            "low_confidence_segments": 0,
        }

    total_duration = sum(s.duration_seconds for s in segments)
    total_words = sum(s.word_count for s in segments)
    confidences = [s.confidence for s in segments if s.confidence > 0]

    avg_confidence = float(np.mean(confidences)) if confidences else 0.0
    low_count = sum(1 for s in segments if s.confidence < 0.70)

    return {
        "total_segments": len(segments),
        "total_duration_seconds": total_duration,
        "total_words": total_words,
        "avg_confidence": avg_confidence,
        "low_confidence_segments": low_count,
    }
