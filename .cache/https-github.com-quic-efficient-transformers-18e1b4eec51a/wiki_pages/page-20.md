# QEfficientMPT Notebook
## Overview
The QEfficientMPT notebook provides an in-depth look at the QEfficient library, focusing on efficient inference on Qualcomm Cloud AI 100 using Hugging Face Transformer models. This notebook serves as a comprehensive guide to leveraging the QEfficient library for optimal performance.

## Key Components / Concepts
The QEfficientMPT notebook utilizes several key components from the QEfficient library, including:
- `QEffAutoPeftModelForCausalLM` and `QEffPeftModelForCausalLM` for causal language models, which are essential for natural language processing tasks
- `QEFFAutoModel` for manipulating transformer models from the Hugging Face hub, allowing for seamless integration with various model architectures
- `SpDPerfMetrics` and `SpDCloudAI100ExecInfo` classes for performance metrics and execution information, providing valuable insights into model performance and execution details

## How it Works
The notebook demonstrates the process of using the QEfficient library to perform efficient inference on Qualcomm Cloud AI 100. It showcases the usage of various models, including `QEffAutoPeftModelForCausalLM` and `QEffPeftModelForCausalLM`, and how to compile and execute them using the `QEFFAutoModel` class. This involves initializing models, compiling them for Cloud AI 100, and running inference sessions using the compiled models.

## Example(s)
The notebook provides concrete examples of how to use the QEfficient library, including:
- Initializing and compiling models for Cloud AI 100, which involves selecting the appropriate model architecture and configuring it for optimal performance
- Running inference sessions using the compiled models, which demonstrates how to leverage the compiled models for efficient inference
- Calculating performance metrics using the `SpDPerfMetrics` class, which provides a way to evaluate model performance and identify areas for improvement

## Diagram(s)
```mermaid
flowchart LR
    A[QEfficient Library] -->|Imports|> B[QEffAutoPeftModelForCausalLM]
    A -->|Imports|> C[QEffPeftModelForCausalLM]
    B -->|Compiles|> D[QEFFAutoModel]
    C -->|Compiles|> D
    D -->|Executes|> E[Inference Session]
    E -->|Calculates|> F[SpDPerfMetrics]
```
Caption: QEfficientMPT Notebook Flowchart, illustrating the key components and workflow of the QEfficientMPT notebook.

## References
- `QEfficient/peft/__init__.py`
- `pyproject.toml`
- `tests/transformers/models/test_causal_lm_models.py`
- `examples/draft_spd_inference.py`