import dataclasses
from typing import Any, Dict

@dataclasses.dataclass(frozen=True)
class BuildResultDto:
    is_success: bool
    error_message: str|None = dataclasses.field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "IsSuccess": self.is_success,
            "ErrorMessage": self.error_message
        }