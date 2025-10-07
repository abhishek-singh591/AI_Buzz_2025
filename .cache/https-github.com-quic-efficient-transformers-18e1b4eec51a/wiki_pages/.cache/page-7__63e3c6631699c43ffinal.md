# Cloud Testing
## Overview
Cloud testing is a crucial aspect of ensuring the reliability and performance of cloud-related functionality in the Efficient Transformers Wiki, specifically within the `Efficient Transformers Wiki` repository. This section provides an overview of the cloud testing process, key components, and how it works, referencing files such as `tests/cloud/test_infer.py` and `QEfficient/generation/text_generation_inference.py`.

## Key Components / Concepts
The key components involved in cloud testing include:
* Cloud AI 100 models
* QPC compilation
* Performance metrics
* Test cases for infer, export, compile, and execute operations, as seen in `tests/transformers/spd/test_pld_inference.py`.

## How it Works
The cloud testing process involves running test cases on Cloud AI 100 models to validate their performance and functionality. The tests cover various scenarios, including inference without and with full batch size, and with and without QNN acceleration, utilizing files like `examples/draft_spd_inference.py` for reference.

## Example(s)
An example of cloud testing can be seen in the `tests/cloud/test_infer.py` file, which contains test cases for the QEfficient cloud infer API, demonstrating how to validate the performance of Cloud AI 100 models.

## Diagram(s)
```mermaid
graph TD
    A[Cloud AI 100 Model] -->|QPC Compilation|> B[Compiled Model]
    B -->|Inference|> C[Output]
    C -->|Performance Metrics|> D[Validation]
    D -->|Test Cases|> E[Cloud Testing]
```
Caption: Cloud Testing Process

## References
* `tests/cloud/test_infer.py`
* `QEfficient/generation/text_generation_inference.py`
* `tests/transformers/spd/test_pld_inference.py`
* `examples/draft_spd_inference.py`