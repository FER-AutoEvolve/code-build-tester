import dataclasses
from fastapi import FastAPI
from code_building import CodeBuilder
from configuration import FastApiConfiguration
from core import Result, Unit
import uvicorn
import logging
import threading
from api_server.dtos import BuildResultDto
import keypoint_notification
import experiment_notification

@dataclasses.dataclass(frozen=False)
class ApiServer:
    _is_task_running: bool = dataclasses.field(default=False, init=False)
    _apiConfiguration: FastApiConfiguration
    _code_builder: CodeBuilder
    _server: uvicorn.Server | None = dataclasses.field(default=None, init=False)
    _logger: logging.Logger = dataclasses.field(default=logging.getLogger())
    _app: FastAPI = dataclasses.field(default_factory=lambda: FastAPI(), init=False)
    _server_thread: threading.Thread | None = dataclasses.field(default=None, init=False)

    def start_server(self) -> Result[Unit]:
        '''
        Starts the FastAPI server in separate thread.
        Returns:
            Result[Unit]: Result indicating success or failure.
        '''
        try:
            self._define_endpoints()
            server_config = uvicorn.Config(app=self._app, host=self._apiConfiguration.host, port=self._apiConfiguration.port, log_level=self._logger.level)
            self._server = uvicorn.Server(config=server_config)
            self._server_thread = threading.Thread(target=self._server.run, daemon=True)
            self._server_thread.start()
            return Result.ok(Unit())
        except Exception as e:
            return Result.err(str(e))
        
    def wait_for_server_to_stop(self) -> Result[Unit]:
        '''
        Waits for the FastAPI server to stop.
        Returns:
            Result[Unit]: Result indicating success or failure.
        '''
        try:
            if self._server_thread and self._server_thread.is_alive():
                self._server_thread.join()
            return Result.ok(Unit())
        except Exception as e:
            return Result.err(str(e))

    def stop_server(self) -> Result[Unit]:
        '''
        Stops the FastAPI server
        Returns:
            Result[Unit]: Result indicating success or failure.
        '''
        try:
            # stop the server
            if self._server:
                self._server.should_exit = True
            if self._server_thread:
                self._server_thread.join()
            return Result.ok(Unit())
        except Exception as e:
            return Result.err(str(e))

    def _define_endpoints(self) -> None:
        '''
        Defines the FastAPI endpoints
        '''
    
        @self._app.get("/health")
        async def _health():
            '''Responds if the server is running'''
            return {"status": "healthy"}

        @self._app.get("/try-build")
        async def _try_build_code():
            '''Handles build requests
             Returns:
                 dict: A dictionary indicating success or failure.
            '''
            self._logger.info(f"Received build request. Starting build procedure...")
            
            self._logger.keypoint(f"Received build request", event_type=keypoint_notification.EventTypes.INFO)
            self._logger.experiment(
                experiment_notification.format_experiment_event_message("REQ_TO_TESTBUILDER_RECEIVED"),
                event_type=experiment_notification.ExperimentEventTypes.INFO,
            )

            self._logger.experiment(
                experiment_notification.format_experiment_event_message("CODE_IN_BUILDTESTING"),
                event_type=experiment_notification.ExperimentEventTypes.INFO,
            )

            res_build = self._code_builder.build()
            build_result_dto: BuildResultDto = BuildResultDto(True, None) if res_build.is_ok() else BuildResultDto(False, res_build.message)

            completed_payload = {
                "status": "SUCCESS" if res_build.is_ok() else "FAILURE",
                "message": res_build.message if res_build.is_err() else "Build succeeded",
            }

            self._logger.experiment(
                experiment_notification.format_experiment_event_message("COMPLETED", completed_payload),
                event_type=experiment_notification.ExperimentEventTypes.SUCCESS if res_build.is_ok() else experiment_notification.ExperimentEventTypes.FAILURE,
            )

            self._logger.experiment(
                experiment_notification.format_experiment_event_message("REQ_TO_OVERSEER_SENT", build_result_dto.to_dict()),
                event_type=experiment_notification.ExperimentEventTypes.INFO,
            )

            if res_build.is_err():
                self._logger.keypoint(f"Code build failed", event_type=keypoint_notification.EventTypes.FAILURE)
            else:
                self._logger.keypoint(f"Code build succeeded", event_type=keypoint_notification.EventTypes.SUCCESS)

            return build_result_dto.to_dict()
