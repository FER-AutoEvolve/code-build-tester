from abc import abstractmethod
import logging
from code_building.configuration import CodeBuilderConfiguration, CodeBuilderTypes
import dataclasses
from core import Result, Unit

@dataclasses.dataclass
class CodeBuilder:
    _configuration: CodeBuilderConfiguration
    _logger: logging.Logger = dataclasses.field(default=logging.getLogger())

    @abstractmethod
    def build(self) -> Result[Unit]:
        pass

    @staticmethod
    def get_code_builder(configuration: CodeBuilderConfiguration) -> Result['CodeBuilder']:
        from code_building.npm_vite_building import NpmViteCodeBuilder
        if configuration.code_builder_type == CodeBuilderTypes.NPM_VITE:
            return Result.ok(NpmViteCodeBuilder(configuration))
        else:
            return Result.err("Unknown code builder type")
            
