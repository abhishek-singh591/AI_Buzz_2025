# Readthedocs Configuration
## Overview
The Readthedocs configuration is defined in the `.readthedocs.yaml` file, located in the root directory of the Flask Wiki repository. This file is used to configure the build process for Read the Docs, a documentation hosting platform.

## Key Components / Concepts
The key components of the Readthedocs configuration include:
* The operating system and Python version to use for the build, specified in the `build` section of the `.readthedocs.yaml` file
* The installation of the 'uv' plugin and setting it as the global default, achieved through the `asdf` commands
* The definition of a command to run the Sphinx documentation builder to generate HTML output, using the `sphinx-build` command

## How it Works
The Readthedocs configuration works by specifying the build environment and the commands to run during the build process. The `.readthedocs.yaml` file defines the operating system and Python version to use, installs the required plugins, and runs the Sphinx documentation builder to generate HTML output. The build process is triggered when the documentation is updated, and the resulting HTML output is hosted on Read the Docs.

## Example(s)
An example of a Readthedocs configuration file is shown in the `.readthedocs.yaml` file:
```yml
version: 2
build:
  os: ubuntu-24.04
  tools:
    python: '3.13'
  commands:
    - asdf plugin add uv
    - asdf install uv latest
    - asdf global uv latest
    - uv run --group docs sphinx-build -W -b dirhtml docs $READTHEDOCS_OUTPUT/html
```
This configuration file specifies the build environment, installs the 'uv' plugin, and runs the Sphinx documentation builder to generate HTML output.

## Diagram(s)
```mermaid
graph TD
    A[.readthedocs.yaml] -->|defines|> B[Build Environment]
    B -->|installs|> C[uv plugin]
    C -->|runs|> D[Sphinx Documentation Builder]
    D -->|generates|> E[HTML Output]
    E -->|hosts|> F[Read the Docs]
```
Readthedocs Configuration Flowchart

## References
* `docs/.readthedocs.yaml`
* `pyproject.toml`
* `tests/test_config.py`
* `docs/conf.py`