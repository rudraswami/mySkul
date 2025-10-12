"""Deterministic job handlers for the demo media pipeline."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Dict

from .manager import JobContext, JobHandler
from .models import JobType

LOGGER = logging.getLogger("jobs.handlers")


def _hash_payload(payload: Dict[str, object]) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


async def analyze_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    source_text = str(payload.get("text", ""))
    token_count = len(source_text.split())
    digest = _hash_payload(payload)
    LOGGER.info("analyze_handler", extra={"job_id": ctx.record.id, "token_count": token_count})
    return {
        "summary": source_text[:256],
        "token_count": token_count,
        "content_hash": digest,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def analyze_scenes_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    scenes = payload.get("scenes") or []
    normalized = [
        {
            "scene": index + 1,
            "description": str(scene).strip(),
            "hash": hashlib.sha1(str(scene).encode("utf-8")).hexdigest(),
        }
        for index, scene in enumerate(scenes)
    ]
    LOGGER.info("analyze_scenes_handler", extra={"job_id": ctx.record.id, "scenes": len(normalized)})
    return {"scenes": normalized}


async def generate_script_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    outline = payload.get("outline") or []
    script_lines = [
        {
            "order": idx + 1,
            "line": f"Scene {idx + 1}: {item.get('description', 'TBD')}"
            if isinstance(item, dict)
            else f"Scene {idx + 1}: {item}",
        }
        for idx, item in enumerate(outline)
    ]
    LOGGER.info("generate_script_handler", extra={"job_id": ctx.record.id, "lines": len(script_lines)})
    return {"script": script_lines}


async def generate_storyboard_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    script = payload.get("script") or []
    frames = [
        {
            "frame": index + 1,
            "caption": entry.get("line", ""),
            "reference": hashlib.md5(entry.get("line", "").encode("utf-8")).hexdigest(),
        }
        for index, entry in enumerate(script)
        if isinstance(entry, dict)
    ]
    LOGGER.info("generate_storyboard_handler", extra={"job_id": ctx.record.id, "frames": len(frames)})
    return {"frames": frames}


async def generate_audio_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    script_lines = payload.get("script") or []
    duration_seconds = 2 * len(script_lines)
    checksum = _hash_payload(payload)
    LOGGER.info("generate_audio_handler", extra={"job_id": ctx.record.id, "duration": duration_seconds})
    return {
        "audio_path": f"/api/uploads/audio/{ctx.record.project_id}/{ctx.record.fingerprint}.mp3",
        "duration_seconds": duration_seconds,
        "content_hash": checksum,
    }


async def generate_video_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    frames = payload.get("frames") or []
    duration_seconds = max(len(frames) * 3, 3)
    LOGGER.info("generate_video_handler", extra={"job_id": ctx.record.id, "duration": duration_seconds})
    return {
        "video_path": f"/api/uploads/video/{ctx.record.project_id}/{ctx.record.fingerprint}.mp4",
        "duration_seconds": duration_seconds,
    }


async def generate_cinematic_handler(ctx: JobContext) -> Dict[str, object]:
    payload = ctx.record.payload
    storyboard_hash = _hash_payload(payload)
    LOGGER.info("generate_cinematic_handler", extra={"job_id": ctx.record.id})
    return {
        "cinematic_path": f"/api/uploads/cinematic/{ctx.record.project_id}/{ctx.record.fingerprint}.mp4",
        "manifest_hash": storyboard_hash,
    }


HANDLERS: Dict[JobType, JobHandler] = {
    JobType.ANALYZE: analyze_handler,
    JobType.ANALYZE_SCENES: analyze_scenes_handler,
    JobType.GENERATE_SCRIPT: generate_script_handler,
    JobType.GENERATE_STORYBOARD: generate_storyboard_handler,
    JobType.GENERATE_AUDIO: generate_audio_handler,
    JobType.GENERATE_VIDEO: generate_video_handler,
    JobType.GENERATE_CINEMATIC: generate_cinematic_handler,
}
