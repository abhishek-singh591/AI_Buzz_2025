# Inference Examples
## Overview
Inference examples using QEfficient are provided in this section. QEfficient is a library interface for efficient inference on Qualcomm Cloud AI 100 using Hugging Face Transformer models.

## Key Components / Concepts
The key components involved in inference using QEfficient include:
- `QEfficient.cloud.infer`: a module containing functions for inference, including `main` and `execute_vlm_model`.
- `QAICInferenceSession`: a class used for running inference sessions.
- `SpDPerfMetrics` and `SpDCloudAI100ExecInfo`: classes used for storing performance metrics and execution information.

## How it Works
Inference using QEfficient involves the following steps:
1. Import necessary modules and classes, including `QEfficient.cloud.infer` and `QAICInferenceSession`.
2. Set up an inference session using `QAICInferenceSession`.
3. Prepare input prompts and model configurations.
4. Run inference using the `execute_vlm_model` function or the `run` method of the `QAICInferenceSession` class.

## Example(s)
Examples of running inference using QEfficient can be found in the `tests/cloud/test_infer.py` and `examples/draft_spd_inference.py` files.

## Diagram(s)
```mermaid
flowchart LR
    A[Prepare Input Prompts] --> B[Set up Inference Session]
    B --> C[Run Inference]
    C --> D[Store Performance Metrics]
    D --> E[Return Execution Information]
```
Caption: High-level flowchart of the inference process using QEfficient.

## References
- `tests/cloud/test_infer.py`
- `examples/draft_spd_inference.py`
- `QEfficient/cloud/infer.py`