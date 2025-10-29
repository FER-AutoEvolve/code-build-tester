import dataclasses
import enum

from core import Result

class CodeBuilderTypes(enum.Enum):
    NPM_VITE = "NPM_VITE"


@dataclasses.dataclass(frozen=True)
class CodeBuilderConfiguration:
    codebase_staging_directory: str
    codebase_directory: str
    codebase_build_directory: str
    code_builder_type: CodeBuilderTypes

    def from_dict(config: dict) -> Result['CodeBuilderConfiguration']:
        try:
            codebase_staging_directory: str = config["CodebaseStagingDirectory"]
            codebase_directory: str = config["CodebaseDirectory"]
            codebase_build_directory: str = config["CodebaseBuildDirectory"]
            code_builder_type: CodeBuilderTypes = CodeBuilderTypes[config["CodeBuilderType"]]

            return Result.ok(CodeBuilderConfiguration(
                codebase_staging_directory=codebase_staging_directory,
                codebase_directory=codebase_directory,
                codebase_build_directory=codebase_build_directory,
                code_builder_type=code_builder_type
            ))
        except Exception as e:
            return Result.err(f"Invalid code builder settings:{e}")
