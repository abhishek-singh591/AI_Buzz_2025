# Jenkinsfile
## Overview
The Jenkinsfile is a crucial component in the deployment process of the Efficient Transformers project. It is a Groovy-based script that defines the Continuous Integration/Continuous Deployment (CI/CD) pipeline for the project.

## Key Components / Concepts
The Jenkinsfile consists of several key components, including:
* **Agent**: Specifies the environment in which the pipeline will run.
* **Stages**: Defines the different stages of the pipeline, such as build, test, and deploy.
* **Steps**: Specifies the actions to be taken within each stage.

## How it Works
The Jenkinsfile works by defining a pipeline that consists of multiple stages. Each stage represents a specific task, such as building the project, running tests, or deploying the application. The pipeline is triggered by a specific event, such as a code commit, and then executes each stage in sequence.

## Example(s)
Here is an example of a simple Jenkinsfile:
```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make test'
            }
        }
        stage('Deploy') {
            steps {
                sh 'make deploy'
            }
        }
    }
}
```
## Diagram(s)
```mermaid
graph LR
    A[Code Commit] --> B[Trigger Pipeline]
    B --> C[Build Stage]
    C --> D[Test Stage]
    D --> E[Deploy Stage]
    E --> F[Deployment]
```
Caption: Jenkinsfile Pipeline Diagram

## References
* `scripts/Jenkinsfile`
* `QEfficient/generation/text_generation_inference.py`
* `QEfficient/compile/compile_helper.py`
* `pyproject.toml`