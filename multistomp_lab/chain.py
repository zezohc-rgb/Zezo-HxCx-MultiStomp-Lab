"""Six-slot patch model. This module does NOT emulate ZDL audio."""
from dataclasses import dataclass, field
import json
from pathlib import Path

MAX_SLOTS = 6

class ChainError(ValueError):
    pass

@dataclass
class Slot:
    zdl_path: str | None = None
    enabled: bool = False
    parameters: dict[str, float] = field(default_factory=dict)
    dsp_cost: float | None = None

    def validate(self):
        if self.zdl_path is not None and (not isinstance(self.zdl_path, str) or not self.zdl_path.lower().endswith(".zdl")):
            raise ChainError("zdl_path must be a .zdl filename or null")
        if not isinstance(self.enabled, bool):
            raise ChainError("enabled must be boolean")
        if not isinstance(self.parameters, dict) or any(not isinstance(k, str) or isinstance(v, bool) or not isinstance(v, (float, int)) for k, v in self.parameters.items()):
            raise ChainError("parameters must map names to numbers")
        if self.dsp_cost is not None and (isinstance(self.dsp_cost, bool) or not isinstance(self.dsp_cost, (int, float)) or not 0 <= self.dsp_cost <= 100):
            raise ChainError("dsp_cost must be between 0 and 100 or unknown")

@dataclass
class Chain:
    slots: list[Slot] = field(default_factory=lambda: [Slot() for _ in range(MAX_SLOTS)])
    name: str = "Untitled"
    format_version: int = 1

    def validate(self):
        if self.format_version != 1 or len(self.slots) != MAX_SLOTS:
            raise ChainError("Only format version 1 with exactly six slots is supported")
        if not isinstance(self.name, str):
            raise ChainError("name must be text")
        for slot in self.slots:
            slot.validate()

    def dsp_report(self):
        self.validate()
        # Allocated effects may use DSP even when bypassed: do not exclude disabled slots.
        loaded = [s for s in self.slots if s.zdl_path is not None]
        known = sum(float(s.dsp_cost) for s in loaded if s.dsp_cost is not None)
        unknown = sum(s.dsp_cost is None for s in loaded)
        return {"known_cost_percent_sum": known, "unknown_effect_count": unknown,
                "complete": unknown == 0, "within_limit": known <= 100 if unknown == 0 else None,
                "warning": "Costs are manually supplied estimates, not measured DSP cycles."}

    def save(self, path):
        from dataclasses import asdict
        self.validate()
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        obj = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(obj, dict) or not isinstance(obj.get("slots"), list):
            raise ChainError("Invalid patch file")
        try:
            chain = cls(slots=[Slot(**s) for s in obj["slots"]], name=obj.get("name", "Untitled"), format_version=obj.get("format_version", 1))
            chain.validate()
        except (TypeError, AttributeError) as exc:
            raise ChainError("Invalid patch fields") from exc
        return chain
