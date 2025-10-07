# Custom Operator Implementations
## Overview
Custom operator implementations are a crucial aspect of the QEfficient library, enabling efficient execution of transformer models on Cloud AI 100 hardware. These custom operators are designed to optimize specific components of the models, such as scatter/gather operations and RMSNorm, to achieve better performance and reduce computational overhead.

## Key Components / Concepts
The custom operator implementations in QEfficient include:
* `ctx_scatter_gather.py`: This module contains the implementation of the custom scatter/gather operator, which is used to efficiently handle tensor operations in the transformer models.
* `ctx_scatter_gather_cb.py`: This module provides a callback function for the custom scatter/gather operator, allowing for flexible and efficient handling of tensor operations.
* `rms_norm.py`: This module implements the custom RMSNorm operator, which is used to normalize the activations of the transformer models.

## How it Works
The custom operator implementations in QEfficient work by replacing the standard PyTorch operators with optimized, custom implementations that are tailored to the specific requirements of the Cloud AI 100 hardware. These custom operators are designed to minimize computational overhead and maximize performance, allowing for efficient execution of transformer models on the target hardware.

## Example(s)
To use the custom operator implementations in QEfficient, you can follow these steps:
1. Import the necessary modules, such as `ctx_scatter_gather` and `rms_norm`.
2. Create an instance of the custom operator, such as `ctx_scatter_gather.CustomScatterGather`.
3. Use the custom operator to perform tensor operations, such as scattering and gathering.

## Diagram(s)
```mermaid
flowchart LR
    A[PyTorch Model] -->|Replace Operators|> B[Custom Operators]
    B -->|Optimize Performance|> C[Cloud AI 100 Hardware]
    C -->|Execute Model|> D[Results]
```
This diagram illustrates the process of replacing standard PyTorch operators with custom operators in QEfficient, which are optimized for the Cloud AI 100 hardware.

## References
* `QEfficient/customop/ctx_scatter_gather.py`
* `QEfficient/customop/ctx_scatter_gather_cb.py`
* `QEfficient/customop/rms_norm.py`
* `QEfficient/transformers/models/modeling_auto.py`
* `QEfficient/exporter/export_hf_to_cloud_ai_100.py`