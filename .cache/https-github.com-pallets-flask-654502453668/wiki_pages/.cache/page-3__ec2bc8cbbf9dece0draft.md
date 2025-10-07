# Installing Flask
## Overview
Flask is a lightweight web application framework designed to make getting started quick and easy, with the ability to scale up to complex applications. It began as a simple wrapper around Werkzeug and Jinja, and has become one of the most popular Python web application frameworks. To install Flask, you will need to have Python and pip installed on your system.

## Key Components / Concepts
The key components of Flask include the Flask application instance, routes, templates, and configuration. The application instance is the core of the Flask application, and is used to configure the application and define routes. Routes are used to map URLs to specific functions in the application, and templates are used to render HTML pages. Configuration is used to customize the behavior of the application.

## How it Works
To install Flask, you can use pip, which is the package installer for Python. The installation process involves downloading and installing the Flask package and its dependencies. The dependencies of Flask include blinker, click, itsdangerous, jinja2, markupsafe, and werkzeug. Once Flask is installed, you can create a new Flask application instance and start building your web application.

## Example(s)
Here is an example of how to install Flask using pip:
```bash
pip install flask
```
Once Flask is installed, you can create a new Flask application instance using the following code:
```python
from flask import Flask
app = Flask(__name__)
```
This code creates a new Flask application instance and assigns it to the variable `app`.

## Diagram(s)
```mermaid
flowchart
    participant User as "User"
    participant Pip as "Pip"
    participant Flask as "Flask"
    participant Dependencies as "Dependencies"

    User->>Pip: Install Flask
    Pip->>Flask: Download and install Flask
    Pip->>Dependencies: Download and install dependencies
    Flask->>User: Create new Flask application instance
```
This diagram shows the process of installing Flask using pip, and creating a new Flask application instance.

## References
* [pyproject.toml](pyproject.toml)
* [tests/test_config.py](tests/test_config.py)
* [tests/test_apps/.flaskenv](tests/test_apps/.flaskenv)
* [README.md](README.md)
* [docs/installation.rst](docs/installation.rst)