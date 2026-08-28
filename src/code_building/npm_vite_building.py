from code_building import CodeBuilder
from core import Result, Unit
import shutil
import subprocess
import pathlib
import experiment_notification

class NpmViteCodeBuilder(CodeBuilder):

    __BUILD_COMMANDS__ = [
        "npm install",
        "npx tsc -p ./tsconfig.json --noEmit --noUnusedLocals false --noUnusedParameters false",
        "npx vite build",
    ]

    def build(self) -> Result[Unit]:
        command_outputs: list[str] = []
        try:
            self._logger.info("Started NPM Vite build procedure")
            self._logger.experiment(
                experiment_notification.format_experiment_event_message("BUILD_STARTED"),
                event_type=experiment_notification.ExperimentEventTypes.INFO,
            )
            # ignore node_modules, dist, folders to get a clean build
            ignore=shutil.ignore_patterns('node_modules', 'dist', '.git')
            # copy all files in tree from codebase to codebase_build
            shutil.copytree(self._configuration.codebase_directory, self._configuration.codebase_build_directory, dirs_exist_ok=True, ignore=ignore)
            self._logger.info("Copied codebase files to build directory")
            # copy all files in tree from codebase_staging to codebase_build
            shutil.copytree(self._configuration.codebase_staging_directory, self._configuration.codebase_build_directory, dirs_exist_ok=True, ignore=ignore)
            self._logger.info("Copied staging files to build directory")
            # build with npm using subprocess and accurate return codes
            self._logger.info("Initiating NPM Vite build")

            absolute_build_dir_path = str(pathlib.Path(self._configuration.codebase_build_directory).absolute())
            for cmd in self.__BUILD_COMMANDS__:
                self._logger.info(f"Running: {cmd}")
                proc = subprocess.run(
                    cmd,
                    cwd=absolute_build_dir_path,
                    capture_output=True,
                    text=True,
                    shell=True
                )
                if proc.stdout:
                    stdout = proc.stdout.strip()
                    self._logger.info(stdout)
                    command_outputs.append(stdout)
                if proc.returncode != 0:
                    # Log stderr and fail fast
                    if proc.stderr:
                        stderr = proc.stderr.strip()
                        self._logger.error(stderr)
                        command_outputs.append(stderr)

                    self._logger.experiment(
                        experiment_notification.format_experiment_event_message(
                            "BUILD_COMPLETED",
                            {
                                "status": "FAILURE",
                                "build_output": "\n".join(command_outputs),
                            },
                        ),
                        event_type=experiment_notification.ExperimentEventTypes.FAILURE,
                    )
                    self._logger.error("Build failure")
                    return Result.err(proc.stderr or "Build failed")

            self._logger.info("Build success")
            self._logger.experiment(
                experiment_notification.format_experiment_event_message(
                    "BUILD_COMPLETED",
                    {
                        "status": "SUCCESS",
                        "build_output": "\n".join(command_outputs),
                    },
                ),
                event_type=experiment_notification.ExperimentEventTypes.SUCCESS,
            )
            return Result.ok(Unit())
        except Exception as e:
            self._logger.error(f"Builder failed build with: {e}")
            self._logger.experiment(
                experiment_notification.format_experiment_event_message(
                    "BUILD_COMPLETED",
                    {
                        "status": "FAILURE",
                        "build_output": str(e),
                    },
                ),
                event_type=experiment_notification.ExperimentEventTypes.FAILURE,
            )
            return Result.err(f"Build failed: {e}")
        finally:
            # clean codebase_build even on failures
            try:
                shutil.rmtree(self._configuration.codebase_build_directory)
                self._logger.info("Cleaned up build directory")
            except Exception as cleanup_err:
                self._logger.error(f"Failed to clean build directory: {cleanup_err}")

    