# Template Engine
## Overview
Flask uses the Jinja2 template engine to render templates. This engine provides a powerful way to separate presentation logic from application logic.

## Key Components / Concepts
The key components of the template engine in Flask are:
* `flask.templating.Environment`: The environment in which templates are rendered.
* `flask.render_template`: A function that renders a template with the given context.
* `flask.render_template_string`: A function that renders a template string with the given context.

## How it Works
The template engine works by rendering templates with the given context. The context is a dictionary of variables that are available to the template.

## Example(s)
Here is an example of how to render a template:
```python
from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", name="World")
```
In this example, the `index.html` template is rendered with the variable `name` set to `"World"`.

## Diagram(s)
```mermaid
flowchart
    participant Flask as "Flask App"
    participant Template as "Template Engine"
    participant Render as "Render Template"

    Flask->>Template: Render template
    Template->>Render: Render template with context
    Render->>Flask: Return rendered template
```
This diagram shows the flow of rendering a template in Flask.

## References
* `tests/test_templating.py`
* `src/flask/templating.py`
* `src/flask/helpers.py`