# Template Rendering
## Overview
Template rendering is a crucial aspect of web development, allowing developers to separate presentation logic from application logic. In the context of Flask, template rendering is achieved through the integration of the Jinja2 templating engine. This section will delve into the details of template rendering in Flask, including the key components, how it works, and examples of its usage.

## Key Components / Concepts
The key components involved in template rendering in Flask include:

* **Jinja2**: A templating engine that allows developers to define templates with placeholders for dynamic content.
* **Template Loader**: A component responsible for loading templates from a specified location.
* **Render Template**: A function that renders a template with the provided data.

## How it Works
The process of template rendering in Flask involves the following steps:

1. **Template Loading**: The template loader loads the template from the specified location.
2. **Data Preparation**: The data to be rendered in the template is prepared.
3. **Template Rendering**: The render template function renders the template with the prepared data.
4. **Response Generation**: The rendered template is used to generate a response to the client.

## Example(s)
The following example demonstrates how to render a template in Flask:
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", value=23)
```
In this example, the `index` function renders the `index.html` template with the `value` parameter set to 23.

## Diagram(s)
```mermaid
flowchart LR
    A[Request] -->|1. Receive Request|> B[Flask App]
    B -->|2. Prepare Data|> C[Data Preparation]
    C -->|3. Load Template|> D[Template Loader]
    D -->|4. Render Template|> E[Render Template]
    E -->|5. Generate Response|> F[Response Generation]
    F -->|6. Send Response|> G[Client]
```
This flowchart illustrates the process of template rendering in Flask, from receiving the request to sending the response.

## References
* `tests/test_templating.py`: This file contains examples of template rendering in Flask, including the use of custom template loaders and render template functions.
* `src/flask/templating.py`: This file contains the implementation of the templating engine in Flask, including the template loader and render template functions.
* `docs/templating.rst`: This file contains documentation on templating in Flask, including examples and best practices.
* `docs/patterns/templateinheritance.rst`: This file contains documentation on template inheritance in Flask, including examples and best practices.