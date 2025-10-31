# code-build-tester
The code build tester component repository with dockerization. Accepts a request to build code generated in the codebase staging.

## Run in debug
1. Prepare a `configuration.local.json` file from the example structure in `configuration.json`. 
2. Run in VS Code debugger with the following `.vscode/launch.json`:
```
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: main.py",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/src/main.py",
            "args": [
                "--config", "${workspaceFolder}/configuration.local.json",
                "--log-to-file"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

3. Prepare python venv and install requiremets in it:

    `python -m venv env`

    `./env/Scripts/activate`

    `pip install -r ./requirements.txt`

## Run in docker
> This container is intended to be run as part of a docker compose and not specifically as a standalone container

The Dockerfile contains two stages. The `base` stage only starts the code-build-tester instance and points it to an existing codebase and codebase staging directory; these directories are planned to be in a volume. The `with_codebase` stage copies a codebase in the `./codebase` directory and a `./codebase_staging` directory to the container.

1. Build the Docker image: 

    `docker build -t code-build-tester --build-args PORT=2000 .`

2. Run the Docker container:

    `docker run -d --name code-build-tester -p 2000:2000 code-build-tester`
