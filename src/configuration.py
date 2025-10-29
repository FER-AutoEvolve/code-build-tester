
import dataclasses

from api_server.configuration import FastApiConfiguration
from code_building.configuration import CodeBuilderConfiguration
from core import Result, Unit


@dataclasses.dataclass(frozen=True)
class KeypointNotificationConfiguration:
    ''' Configuration for the keypoint notification system.'''
    enabled: bool
    endpoint: str

    @staticmethod
    def from_dict(config: dict) -> Result['KeypointNotificationConfiguration']:
        ''' 
        Creates a KeypointNotificationConfiguration object from a dictionary.
        Args:
            config (dict): Dictionary containing configuration data.
        Returns:
            Result[KeypointNotificationConfiguration]: Result containing the KeypointNotificationConfiguration object or an error
        '''
        try:
            enabled = config.get("Enabled", True)
            endpoint = config.get("Endpoint", "")
            if not endpoint:
                return Result.err("KeypointNotification configuration requires 'Endpoint' to be set.")
            return Result.ok(KeypointNotificationConfiguration(
                enabled=enabled,
                endpoint=endpoint
            ))
        except ValueError as e:
            return Result.err(f"Invalid keypoint notification configuration: {e}")
        
@dataclasses.dataclass(frozen=True)
class Configuration:
    ''' Configuration for the entire application.'''
    fast_api_config: FastApiConfiguration
    code_builder_config: CodeBuilderConfiguration
    keypoint_notification_config: KeypointNotificationConfiguration | None = dataclasses.field(default=None)

    @staticmethod
    def from_dict(config: dict) -> Result['Configuration']:
        ''' 
        Creates a Configuration object from a dictionary.
        Args:
            config (dict): Dictionary containing configuration data.
        Returns:
            Result[Configuration]: Result containing the Configuration object or an error message.
        '''
        try:
            res_fast_api_config = FastApiConfiguration.from_dict(config.get("FastApi", {}))
            res_keypoint_notification_config = KeypointNotificationConfiguration.from_dict(config.get("KeypointNotification")) if config.get("KeypointNotification", None) else Result.ok(Unit())
            res_code_builder_config = CodeBuilderConfiguration.from_dict(config.get("CodeBuilder"))
            if res_fast_api_config.is_err():
                return Result.err(res_fast_api_config.message)
            if res_code_builder_config.is_err():
                return Result.err(res_code_builder_config.message)
            if res_keypoint_notification_config.is_err():
                return Result.err(res_keypoint_notification_config.message)
            
            return Result.ok(Configuration(
                fast_api_config=res_fast_api_config.value,
                code_builder_config=res_code_builder_config.value,
                keypoint_notification_config=res_keypoint_notification_config.value if res_keypoint_notification_config.value != Unit() else None
            ))
        
        except ValueError as e:
            return Result.err(f"Invalid configuration: {e}")