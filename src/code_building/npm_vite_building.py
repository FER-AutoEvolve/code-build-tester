from code_building import CodeBuilder
from core import Result, Unit
import shutil

class NpmViteCodeBuilder(CodeBuilder):

    def build(self) -> Result[Unit]:
        try:
            self._logger.info("Started NPM Vite build procedure")
            # copy all files in tree from codebase to codebase_build
            shutil.copytree(self._configuration.codebase_directory, self._configuration.codebase_build_directory, dirs_exist_ok=True)
            self._logger.info("Copied codebase files to build directory")
            # copy all files in tree from codebase_staging to codebase_build
            shutil.copytree(self._configuration.codebase_staging_directory, self._configuration.codebase_build_directory, dirs_exist_ok=True)
            self._logger.info("Copied staging files to build directory")
            # build with npm and listen to the print
            self._logger.info("Initiating NPM Vite build")
            import os
            build_output = os.popen(f"cd {self._configuration.codebase_build_directory} && npm run build").read()
            # determine if print is failure or success
            build_output_lowered = build_output.lower()
            res_build: Result[Unit] = \
            Result.err(build_output) if "fail" in  build_output_lowered or "error" in build_output_lowered else Result.ok(Unit())
            if res_build.is_err():
                self._logger.error("Build failure")
            else:
                self._logger.info("Build success")
            # clean codebase_build
            shutil.rmtree(self._configuration.codebase_build_directory)
            self._logger.info("Cleaned up build directory")

            return res_build
        except Exception as e:
            self._logger.error(f"Builder failed build with: {e}")
            return Result.err(f"Build failed: {e}")

    