# Introduction to Scripts
The Efficient Transformers Wiki repository contains a variety of scripts that support the development, testing, and deployment of efficient transformer models. These scripts are essential for tasks such as model training, evaluation, and inference.

## Overview
The scripts in the repository are organized into several categories, including model training, evaluation, and inference. Each script is designed to perform a specific task, such as training a model, computing perplexity, or generating text.

## Key Components / Concepts
The scripts in the repository rely on several key components and concepts, including:
* Model architectures: The repository supports a range of model architectures, including transformer-based models.
* Training and evaluation: The scripts provide tools for training and evaluating models on various datasets.
* Inference: The scripts support inference tasks, such as text generation and classification.

## How it Works
The scripts in the repository work together to support the development and deployment of efficient transformer models. For example, the training scripts can be used to train a model, which can then be evaluated using the evaluation scripts. The inference scripts can be used to generate text or perform other inference tasks.

## Example(s)
One example of a script in the repository is the `draft_spd_inference.py` script, which is used for semantic search and inference tasks. This script takes in a dictionary of inputs, a prefill sequence length, and a slot index, and returns a `SpDCloudAI100ExecInfo` object containing performance metrics, generated text, and other relevant information.

## Diagram(s)
```mermaid
flowchart LR
    A[Model Training] --> B[Model Evaluation]
    B --> C[Inference]
    C --> D[Text Generation]
    D --> E[Performance Metrics]
```
This flowchart illustrates the workflow of the scripts in the repository, from model training to text generation and performance metrics.

## References
* `tests/README.md`
* `QEfficient/__init__.py`
* `examples/draft_spd_inference.py`
* `QEfficient/generation/text_generation_inference.py`