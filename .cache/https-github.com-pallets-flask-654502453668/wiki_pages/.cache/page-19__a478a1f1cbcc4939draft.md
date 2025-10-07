# Routing and URL Building
## Overview
Flask provides a flexible way to build URLs and route requests to specific functions. This is achieved through the use of the `@app.route()` decorator, which maps a URL to a specific function in the application.

## Key Components / Concepts
The key components involved in routing and URL building in Flask are:
* `@app.route()`: a decorator used to map a URL to a specific function
* `flask.url_for()`: a function used to generate URLs for routes in the application

## How it Works
When a request is made to the application, Flask uses the `@app.route()` decorator to determine which function to call. The `flask.url_for()` function is used to generate URLs for routes in the application.

## Example(s)
For example, to map the root URL of the application to a function called `index()`, you would use the following code:
```python
@app.route("/")
def index():
    return "Hello, World!"
```
To generate a URL for the `index()` function, you would use the following code:
```python
url = flask.url_for("index")
```
## Diagram(s)
```mermaid
flowchart
    participant Client as "Client"
    participant Flask as "Flask"
    participant Function as "Function"

    Client->>Flask: Request
    Flask->>Function: Call function
    Function->>Flask: Return response
    Flask->>Client: Return response
```
This diagram shows the flow of a request through the application, from the client to the Flask application, and then to the specific function that handles the request.

## References
* `tests/test_appctx.py`
* `tests/test_blueprints.py`
* `tests/test_helpers.py`
* `docs/patterns/templateinheritance.rst`
* `docs/patterns/urlprocessors.rst`