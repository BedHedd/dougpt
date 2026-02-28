"""
Path discovery helpers for ASR audio prep pipeline.

Mirrors the pattern from chat-extraction/chat-extraction.py for locating
00-supporting-files and large-files directories, keeping scripts relocatable
across worktrees.
"""

from pathlib import Path
from typing import Optional

from loguru import logger


def _find_ancestor_with_marker(start: Path, marker: str) -> Optional[Path]:
    """Walk up from start looking for a directory containing marker."""
    for parent in start.parents:
        if (parent / marker).exists():
            return parent / marker
    return None


def _find_project_root(start: Path) -> Path:
    """Find project root by locating 00-supporting-files directory."""
    supporting = _find_ancestor_with_marker(start, "00-supporting-files")
    if supporting is None:
        raise RuntimeError(
            f"Could not find '00-supporting-files' directory from {start}. "
            "Ensure you're running from within the project structure."
        )
    return supporting.parent


# Resolve paths at import time for convenience
try:
    _start = Path(__file__).resolve()
except NameError:
    _start = Path.cwd()

_project_root = _find_project_root(_start)

#: Project root directory (dougpt/)
project_parent: Path = _project_root

#: Path to 00-supporting-files/
supporting_files: Path = _project_root / "00-supporting-files"

#: Path to data directory under supporting_files
data_dir: Path = supporting_files / "data"

#: Path to transcripts output directory
transcripts_dir: Path = data_dir / "transcripts"

#: Path to large-files directory (video sources)
large_files_dir: Path = _project_root / "large-files"

#: Path to temp directory for intermediate files
temp_dir: Path = data_dir / "temp"


def resolve_transcript_dir(source_id: str, create: bool = True) -> Path:
    """
    Resolve the transcript output directory for a given source_id.

    Args:
        source_id: Unique identifier for the source video/audio
        create: If True, create the directory if it doesn't exist

    Returns:
        Path to the transcript directory for this source

    Example:
        >>> resolve_transcript_dir("VpmmuHlLPM0")
        PosixPath('.../00-supporting-files/data/transcripts/VpmmuHlLPM0')
    """
    output_dir = transcripts_dir / source_id
    if create and not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created transcript directory: {output_dir}")
    return output_dir


def resolve_large_file(filename: str) -> Optional[Path]:
    """
    Resolve a file in the large-files directory.

    Args:
        filename: Name of the file to locate

    Returns:
        Path to the file if it exists, None otherwise
    """
    filepath = large_files_dir / filename
    if filepath.exists():
        return filepath
    logger.warning(f"File not found in large-files: {filepath}")
    return None


def ensure_temp_dir() -> Path:
    """
    Ensure the temp directory exists and return its path.

    Returns:
        Path to the temp directory
    """
    if not temp_dir.exists():
        temp_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Created temp directory: {temp_dir}")
    return temp_dir


def check_rocm_visibility() -> bool:
    """
    Check if ROCm GPU is visible and log status.

    Returns:
        True if ROCm GPU appears available, False otherwise
    """
    import os

    # Check for ROCm visibility
    hip_visible = os.environ.get("HIP_VISIBLE_DEVICES", "")
    cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")

    # Check for AMD GPU via /sys
    amd_gpu_exists = Path("/sys/class/drm").exists() and any(
        (Path("/sys/class/drm") / d).exists()
        for d in (Path("/sys/class/drm").iterdir() if Path("/sys/class/drm").exists() else [])
        if "card" in str(d) or "render" in str(d)
    )

    # Try to import torch and check for ROCm
    torch_rocm = False
    try:
        import torch

        if hasattr(torch.version, "hip") and torch.version.hip is not None:
            torch_rocm = True
            logger.info(f"PyTorch ROCm detected: HIP version {torch.version.hip}")
            if torch.cuda.is_available():
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
    except ImportError:
        logger.debug("PyTorch not installed - skipping ROCm check")
    except Exception as e:
        logger.warning(f"Error checking PyTorch ROCm: {e}")

    rocm_available = bool(hip_visible) or torch_rocm or amd_gpu_exists

    if rocm_available:
        logger.info("ROCm GPU environment detected")
    else:
        logger.warning(
            "No ROCm GPU environment detected. "
            "Audio prep will work but separation may fall back to CPU."
        )

    return rocm_available


# Log ROCm status on import (non-blocking)
try:
    check_rocm_visibility()
except Exception as e:
    logger.debug(f"ROCm visibility check skipped: {e}")
