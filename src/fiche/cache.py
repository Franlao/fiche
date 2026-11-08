"""Cache disque par empreinte de l'entrée : rejouer une fiche ne repaie aucun appel."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


class DiskCache:
    def __init__(self, root: Path, enabled: bool = True) -> None:
        self.root = root
        self.enabled = enabled
        if enabled:
            root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def key(namespace: str, payload: Any) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return namespace + "-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]

    def get(self, key: str) -> Any | None:
        if not self.enabled:
            return None
        path = self.root / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def set(self, key: str, value: Any) -> None:
        if self.enabled:
            (self.root / f"{key}.json").write_text(
                json.dumps(value, ensure_ascii=False, default=str), encoding="utf-8"
            )
