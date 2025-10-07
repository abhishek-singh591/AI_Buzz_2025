# Request and Response Objects
## Overview
Flask provides a request object to handle HTTP requests and a response object to handle HTTP responses. These objects are crucial in handling HTTP requests and responses in a Flask application.

## Key Components / Concepts
The request object provides information about the HTTP request, such as the request method, path, and headers. The response object, on the other hand, is used to generate HTTP responses, including setting the status code, headers, and response body.

## How it Works
When a request is made to a Flask application, the request object is created and passed to the view function. The view function can then use the request object to access information about the request. After processing the request, the view function returns a response object, which is then sent back to the client.

## Example(s)
Here's an example of how to use the request and response objects in a Flask view function:
```python
from flask import Flask, request, Response

app = Flask(__name__)

@app.route('/')
def index():
    # Access the request object
    method = request.method
    path = request.path

    # Create a response object
    response = Response('Hello, World!', status=200)

    # Set custom headers
    response.headers['X-Method'] = method

    return response
```

## Diagram(s)
```mermaid
flowchart
    participant Client as "Client"
    participant Flask as "Flask"
    participant View as "View Function"
    participant Request as "Request Object"
    participant Response as "Response Object"

    Client->>Flask: Send HTTP Request
    Flask->>Request: Create Request Object
    Flask->>View: Call View Function
    View->>Request: Access Request Object
    View->>Response: Create Response Object
    View->>Response: Set Response Status Code and Headers
    Response->>Flask: Return Response Object
    Flask->>Client: Send HTTP Response
```
Request and Response Object Flowchart

## References
* `tests/test_basic.py`
* `tests/test_views.py`
* `tests/test_templating.py`
* `docs/reqcontext.rst`