# Docker Deployment
## Overview
The Efficient Transformers library can be deployed using Docker, which provides a consistent and reliable environment for building and running the application. The Dockerfile, located at `./Dockerfile`, is used to create a Docker image that includes all the necessary dependencies and configurations specified in `pyproject.toml`.

## Key Components / Concepts
The key components of the Docker deployment are:
* Dockerfile: The Dockerfile is used to create a Docker image that includes all the necessary dependencies and configurations.
* Docker image: The Docker image is created by building the Dockerfile and includes all the necessary dependencies and configurations.
* Docker container: The Docker container is created by running the Docker image and provides a consistent and reliable environment for building and running the application.

## How it Works
The Docker deployment works as follows:
1. The Dockerfile is used to create a Docker image that includes all the necessary dependencies and configurations.
2. The Docker image is built by running the command `docker build -t efficient-transformers .` in the directory where the Dockerfile is located.
3. The Docker container is created by running the command `docker run -it efficient-transformers` and provides a consistent and reliable environment for building and running the application.

## Example(s)
An example of how to deploy the Efficient Transformers library using Docker is as follows:
```bash
# Build the Docker image
docker build -t efficient-transformers .

# Run the Docker container
docker run -it efficient-transformers
```

## Diagram(s)
```mermaid
graph LR
    A[Dockerfile] -->|Build|> B[Docker Image]
    B -->|Run|> C[Docker Container]
    C -->|Deploy|> D[Efficient Transformers Library]
```
Caption: Docker Deployment Diagram

## References
* [./Dockerfile](./Dockerfile)
* [./README.md](./README.md)
* [./pyproject.toml](./pyproject.toml)
* [./QEfficient/transformers/quantizers/auto.py](./QEfficient/transformers/quantizers/auto.py)