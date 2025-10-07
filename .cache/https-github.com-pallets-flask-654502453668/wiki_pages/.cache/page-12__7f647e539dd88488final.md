# Celery Example
## Overview
The Celery example provided in the Flask repository demonstrates how to integrate Celery, a distributed task queue, with a Flask application. This example showcases how to create and run tasks asynchronously in the background.

## Key Components / Concepts
* Celery: a distributed task queue that allows running tasks asynchronously in the background
* Flask: a lightweight web framework for building web applications
* make_celery: a function that creates a Celery instance and configures it to work with the Flask application

## How it Works
1. The `make_celery` function, defined in [examples/celery/make_celery.py](examples/celery/make_celery.py), creates a Celery instance and configures it to work with the Flask application.
2. Tasks are defined in the [examples/celery/src/task_app/tasks.py](examples/celery/src/task_app/tasks.py) file and can be run asynchronously using the Celery instance.
3. The Flask application can trigger tasks to run in the background using the Celery instance.

## Example(s)
```python
from celery import Celery

celery = Celery(__name__)

@celery.task
def add(x, y):
    return x + y
```

## Diagram(s)
```mermaid
flowchart
    participant Flask as "Flask Application"
    participant Celery as "Celery Instance"
    participant Task as "Task"

    Flask->>Celery: Create Celery instance
    Celery->>Task: Define task
    Flask->>Celery: Trigger task to run
    Celery->>Task: Run task in background
```
Caption: Celery Example Flowchart

## References
* [README.md](README.md)
* [examples/celery/make_celery.py](examples/celery/make_celery.py)
* [examples/celery/src/task_app/tasks.py](examples/celery/src/task_app/tasks.py)