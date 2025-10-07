# Quantization and Compression
## Overview
Quantization and compression are essential techniques in efficient transformer models, enabling reduced memory usage and faster inference times. QEfficient supports various quantization and compression methods to optimize model performance.

## Key Components / Concepts
The key components involved in quantization and compression include:
- Quantization: reducing the precision of model weights and activations
- Compression: reducing the size of model weights and activations

## How it Works
Quantization and compression in QEfficient work by applying transformations to the model weights and activations. This process involves:
1. Quantizing model weights and activations to lower precision (e.g., int8)
2. Compressing the quantized weights and activations using techniques like pruning or knowledge distillation

## Example(s)
An example of quantization in QEfficient can be seen in the `replace_transformers_quantizers` function, which updates the quantization mappings for transformers to enable the use of AWQ/GPTQ models on CPU.

## Diagram(s)
```mermaid
flowchart LR
    A[Model Weights] -->|Quantization|> B[Quantized Weights]
    B -->|Compression|> C[Compressed Weights]
    C -->|Inference|> D[Model Output]
```
Quantization and Compression Flowchart

## References
- `QEfficient/transformers/quantizers/auto.py`
- `QEfficient/transformers/models/modeling_auto.py`
- `QEfficient/transformers/quantizers/quant_transforms.py`
- `QEfficient/transformers/quantizers/quantizer_compressed_tensors.py`