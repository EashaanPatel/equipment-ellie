import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class JsonStore:
    path: Path

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"equipment": [], "people": []}
        return json.loads(self.path.read_text())

    def save(self, data: Dict[str, Any]) -> None:
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True))
