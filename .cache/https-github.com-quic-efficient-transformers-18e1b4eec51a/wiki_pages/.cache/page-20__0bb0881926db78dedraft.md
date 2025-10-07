# QEfficientMPT Notebook
## Overview
The QEfficientMPT notebook is designed to provide an overview of the QEfficient library, specifically for efficient inference on Qualcomm Cloud AI 100 using Hugging Face Transformer models.

## Key Components / Concepts
The QEfficientMPT notebook utilizes various components from the QEfficient library, including:
- QEffAutoPeftModelForCausalLM and QEffPeftModelForCausalLM for causal language models
- QEFFAutoModel for manipulating transformer models from the HuggingFace hub
- SpDPerfMetrics and SpDCloudAI100ExecInfo classes for performance metrics and execution information

## How it Works
The notebook demonstrates how to use the QEfficient library to perform efficient inference on Qualcomm Cloud AI 100. It showcases the usage of various models, including QEffAutoPeftModelForCausalLM and QEffPeftModelForCausalLM, and how to compile and execute them using the QEFFAutoModel class.

## Example(s)
The notebook provides examples of how to use the QEfficient library, including:
- Initializing and compiling models for Cloud AI 100
- Running inference sessions using the compiled models
- Calculating performance metrics using the SpDPerfMetrics class

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
Caption: QEfficientMPT Notebook Flowchart

## References
- `QEfficient/peft/__init__.py`
- `pyproject.toml`
- `tests/transformers/models/test_causal_lm_models.py`
- `examples/draft_spd_inference.py`