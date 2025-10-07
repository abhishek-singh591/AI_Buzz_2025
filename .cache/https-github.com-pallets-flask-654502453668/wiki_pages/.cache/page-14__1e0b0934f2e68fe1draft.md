# Deployment Options
## Overview
Flask is a lightweight web application framework that can be deployed in various ways. This section will cover the deployment options for Flask, including Gunicorn, uWSGI, and Nginx. These tools are essential for running a Flask application in a production environment.

## Key Components / Concepts
To deploy a Flask application, several key components and concepts need to be understood:
* **WSGI**: The Web Server Gateway Interface is a standard for Python web applications to communicate with web servers.
* **Gunicorn**: A WSGI HTTP server that can run Flask applications.
* **uWSGI**: A WSGI server that can run Flask applications and provides additional features such as process management and caching.
* **Nginx**: A web server that can be used as a reverse proxy to serve Flask applications.

## How it Works
The deployment process involves the following steps:
1. **Create a Flask application**: Create a Flask application using the `Flask` class, as shown in the `tests/test_apps/cliapp/inner1/inner2/flask.py` file.
2. **Configure the application**: Configure the application by setting environment variables, such as those defined in the `tests/test_apps/.flaskenv` file.
3. **Run the application with Gunicorn or uWSGI**: Run the application using Gunicorn or uWSGI, which will handle HTTP requests and communicate with the Flask application.
4. **Use Nginx as a reverse proxy**: Use Nginx as a reverse proxy to serve the Flask application, providing additional features such as load balancing and caching.

## Example(s)
An example of running a Flask application with Gunicorn can be found in the `docs/deploying/gunicorn.rst` file. This example shows how to create a Gunicorn configuration file and run the application using the `gunicorn` command.

## Diagram(s)
```mermaid
flowchart
    participant Flask as "Flask Application"
    participant Gunicorn as "Gunicorn"
    participant uWSGI as "uWSGI"
    participant Nginx as "Nginx"
    participant Client as "Client"

    Client->>Nginx: HTTP Request
    Nginx->>Gunicorn: Forward Request
    Gunicorn->>Flask: Handle Request
    Flask->>Gunicorn: Return Response
    Gunicorn->>Nginx: Return Response
    Nginx->>Client: Return Response

    Client->>Nginx: HTTP Request
    Nginx->>uWSGI: Forward Request
    uWSGI->>Flask: Handle Request
    Flask->>uWSGI: Return Response
    uWSGI->>Nginx: Return Response
    Nginx->>Client: Return Response
```
This diagram shows the flow of requests and responses between the client, Nginx, Gunicorn or uWSGI, and the Flask application.

## References
* `tests/test_apps/cliapp/inner1/inner2/flask.py`: An example of creating a Flask application.
* `tests/test_apps/.flaskenv`: An example of configuring environment variables for a Flask application.
* `docs/deploying/gunicorn.rst`: An example of running a Flask application with Gunicorn.
* `docs/deploying/nginx.rst`: An example of using Nginx as a reverse proxy for a Flask application.
* `docs/deploying/uwsgi.rst`: An example of running a Flask application with uWSGI.