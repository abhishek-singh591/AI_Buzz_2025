# Readthedocs Configuration
## Overview
The Readthedocs configuration is defined in the `.readthedocs.yaml` file. This file is used to configure the build process for Read the Docs, a documentation hosting platform.

## Key Components / Concepts
The key components of the Readthedocs configuration include:
* The operating system and Python version to use for the build
* The installation of the 'uv' plugin and setting it as the global default
* The definition of a command to run the Sphinx documentation builder to generate HTML output

## How it Works
The Readthedocs configuration works by specifying the build environment and the commands to run during the build process. The `.readthedocs.yaml` file defines the operating system and Python version to use, installs the required plugins, and runs the Sphinx documentation builder to generate HTML output.

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
## Diagram(s)
```mermaid
graph LR
    A[.readthedocs.yaml] -->|defines|> B[Build Environment]
    B -->|installs|> C[uv plugin]
    C -->|runs|> D[Sphinx Documentation Builder]
    D -->|generates|> E[HTML Output]
```
Readthedocs Configuration Flowchart

## References
* `.readthedocs.yaml`
* `pyproject.toml`
* `tests/test_config.py`