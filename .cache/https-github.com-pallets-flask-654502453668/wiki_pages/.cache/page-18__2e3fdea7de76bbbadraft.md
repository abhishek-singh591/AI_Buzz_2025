# Celery Background Task Example
## Overview
The Celery Background Task Example demonstrates how to configure Celery with Flask, define asynchronous tasks, and create HTTP endpoints for task management. This example is crucial for understanding how to offload computationally expensive tasks from the main application thread, improving overall system responsiveness and scalability.

## Key Components / Concepts
- **Celery**: A distributed task queue that allows running time-consuming tasks asynchronously in the background.
- **Flask**: A micro web framework for building web applications.
- **Celery Worker**: The component responsible for executing tasks.
- **Broker**: The message broker (e.g., RabbitMQ, Redis) that handles task messages.

## How it Works
1. **Task Definition**: Tasks are defined in a separate module (e.g., `tasks.py`) using the `@app.task` decorator provided by Celery.
2. **Celery Configuration**: Celery is configured with Flask by creating a Celery instance and passing the Flask application instance to it.
3. **Task Execution**: When a task is called, it is sent to the broker, which then distributes it to a Celery worker for execution.
4. **Result Storage**: Task results can be stored in a backend (e.g., Redis, database) for later retrieval.

## Example(s)
Consider a simple example where we have a Flask application that uses Celery to run a background task. The task simulates a long-running operation.

```python
from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def long_running_task():
    # Simulate a long-running task
    import time
    time.sleep(10)
    return "Task completed"

@app.route('/run-task', methods=['GET'])
def run_task():
    task = long_running_task.apply_async()
    return f"Task ID: {task.id}"

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    task = long_running_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'status': task.info
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return response
```

## Diagram(s)
```mermaid
flowchart LR
    A[Flask App] -->|Send Task|> B[Celery Broker]
    B -->|Distribute Task|> C[Celery Worker]
    C -->|Execute Task|> D[Task Result]
    D -->|Store Result|> E[Result Backend]
    E -->|Retrieve Result|> A
```
Caption: Overview of the Celery Background Task workflow with Flask.

## References
- `examples/celery/make_celery.py`: An example of how to create a Celery instance with Flask.
- `examples/celery/src/task_app/tasks.py`: Defines tasks that can be executed by Celery.
- `examples/celery/src/task_app/views.py`: Demonstrates how to integrate Celery tasks with Flask views.
- `tests/test_async.py`: Provides examples of testing asynchronous routes and error handling in Flask applications.
- `tests/test_cli.py`: Shows how to create and configure a Flask web application for semantic search.