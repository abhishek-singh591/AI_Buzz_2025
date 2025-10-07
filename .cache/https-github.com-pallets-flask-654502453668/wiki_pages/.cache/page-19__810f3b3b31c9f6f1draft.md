# JavaScript AJAX Example
## Overview
The JavaScript AJAX example demonstrates how to use client-side AJAX interactions to call Flask endpoints. This is achieved using the `fetch` API, jQuery, and XMLHttpRequest (XHR). The example showcases how to send requests to Flask endpoints and handle responses.

## Key Components / Concepts
The key components involved in this example are:
* Flask endpoints: These are the server-side functions that handle requests and return responses.
* Client-side JavaScript: This is used to send requests to the Flask endpoints using AJAX.
* AJAX libraries/frameworks: These include the `fetch` API, jQuery, and XHR, which provide a way to send asynchronous requests to the server.

## How it Works
The process works as follows:
1. The client-side JavaScript code sends an AJAX request to a Flask endpoint.
2. The Flask endpoint handles the request and returns a response.
3. The client-side JavaScript code receives the response and updates the page accordingly.

## Example(s)
For example, consider a Flask endpoint that returns a JSON response:
```python
from flask import jsonify

@app.route('/example', methods=['GET'])
def example():
    return jsonify({'message': 'Hello, World!'})
```
The client-side JavaScript code can use the `fetch` API to send a request to this endpoint:
```javascript
fetch('/example')
  .then(response => response.json())
  .then(data => console.log(data));
```
This will log the JSON response to the console.

## Diagram(s)
```mermaid
flowchart LR
    A[Client-side JavaScript] -->|Send AJAX request|> B[Flask Endpoint]
    B -->|Return response|> A
    A -->|Update page|> C[Web Page]
```
This flowchart shows the process of sending an AJAX request from the client-side JavaScript code to a Flask endpoint and receiving a response.

## References
* `tests/test_blueprints.py`: This file contains examples of Flask endpoints that can be used with AJAX requests.
* `tests/test_basic.py`: This file contains examples of basic Flask endpoints that can be used with AJAX requests.
* `examples/javascript/js_example/views.py`: This file contains examples of Flask endpoints that can be used with AJAX requests in a JavaScript context.
* `examples/javascript/js_example/templates/fetch.html`: This file contains an example of using the `fetch` API to send an AJAX request to a Flask endpoint.
* `examples/javascript/js_example/templates/jquery.html`: This file contains an example of using jQuery to send an AJAX request to a Flask endpoint.