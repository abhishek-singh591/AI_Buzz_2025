# Template Engine
## Overview
Flask uses the Jinja2 template engine to render templates, providing a powerful way to separate presentation logic from application logic. This is achieved through the `flask.templating` module, which is responsible for rendering templates.

## Key Components / Concepts
The key components of the template engine in Flask are:
* `flask.templating.Environment`: The environment in which templates are rendered, configured in `src/flask/templating.py`.
* `flask.render_template`: A function that renders a template with the given context, defined in `src/flask/helpers.py`.
* `flask.render_template_string`: A function that renders a template string with the given context, also defined in `src/flask/helpers.py`.

## How it Works
The template engine works by rendering templates with the given context. The context is a dictionary of variables that are available to the template. This process is initiated by the `flask.render_template` function, which is demonstrated in the example below.

## Example(s)
Here is an example of how to render a template:
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", name="World")
```
In this example, the `index.html` template is rendered with the variable `name` set to `"World"`. The `render_template` function is used to render the template, and the resulting HTML is returned to the client.

## Diagram(s)
```mermaid
flowchart
    participant Flask as "Flask App"
    participant Template as "Template Engine"
    participant Render as "Render Template"

    Flask->>Template: Render template request
    Template->>Render: Render template with context
    Render->>Template: Return rendered template
    Template->>Flask: Return rendered template to Flask
```
This diagram shows the flow of rendering a template in Flask, from the initial request to the final rendered template.

## References
* `tests/test_templating.py`
* `src/flask/templating.py`
* `src/flask/helpers.py`
* `docs/core_features/template_engine.md`