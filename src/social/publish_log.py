import json
import os
from datetime import datetime, timezone


def append_publish_event(base_dir: str, mode: str, text: str, results: list[dict], image_used: bool):
    """Guarda eventos de publicación en un JSON estructurado y extensible."""
    path = os.path.join(base_dir, "data", "publish_history.json")

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        payload = {
            "version": 1,
            "events": [],
            "stats": {"total_events": 0, "successful_events": 0},
        }

    success = any(r.get("success") for r in results)
    event = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "image_used": image_used,
        "text_preview": text[:240],
        "results": results,
        "success": success,
    }

    payload["events"].append(event)
    payload["stats"]["total_events"] += 1
    if success:
        payload["stats"]["successful_events"] += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

