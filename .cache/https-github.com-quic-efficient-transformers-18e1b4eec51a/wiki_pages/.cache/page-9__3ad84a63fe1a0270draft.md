# Quantization Support
## Overview
Quantization is a critical component in optimizing deep learning models for efficient deployment on various hardware platforms. The QEfficient library provides built-in support for quantization through multiple back-ends, including AWQ (Adaptive Weight Quantization), GPTQ (Generalized Post-Training Quantization), and FP8 (8-bit Floating Point). This support enables users to apply quantization to their models, significantly reducing the memory footprint and computational requirements without substantial loss in model accuracy.

## Key Components / Concepts
- **AWQ (Adaptive Weight Quantization):** AWQ is a quantization technique that adapts the quantization scheme based on the model's weights, aiming to minimize the loss in accuracy due to quantization.
- **GPTQ (Generalized Post-Training Quantization):** GPTQ is a method designed for quantizing transformer models. It involves learning the optimal quantization points post-training to maintain model performance.
- **FP8 (8-bit Floating Point):** FP8 is a floating-point format that uses 8 bits to represent numbers, offering a significant reduction in memory usage and computational intensity compared to the standard 32-bit floating-point format.

## How it Works
The quantization process in QEfficient involves several steps:
1. **Model Preparation:** The user selects a model to be quantized. This could be any transformer-based model supported by the Hugging Face ecosystem.
2. **Quantization Backend Selection:** The user chooses a quantization backend (AWQ, GPTQ, or FP8) based on their specific requirements and the characteristics of the model.
3. **Quantization:** The selected quantization backend applies its quantization algorithm to the model. This involves converting the model's weights and, in some cases, activations to the chosen quantized format.
4. **Model Compilation:** After quantization, the model is compiled into an optimized form that can be executed efficiently on the target hardware. This step may involve additional optimizations such as knowledge distillation or pruning.
5. **Deployment:** The quantized and compiled model is then deployed on the target hardware, where it can be used for inference.

## Example(s)
To quantize a model using QEfficient, you might follow these steps:
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Load a pre-trained model and tokenizer
model = QEFFAutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", pooling="mean")
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Compile the model with quantization
model.compile(num_cores=16, quantization="awq")

# Prepare input
inputs = tokenizer("My name is", return_tensors="pt")

# Generate output
output = model.generate(inputs)
print(output)
```

## Diagram(s)
```mermaid
flowchart LR
    A[Model Selection] -->|Choose Model|> B[Quantization Backend Selection]
    B -->|Select Quantization Method|> C[Quantization]
    C -->|Apply Quantization|> D[Model Compilation]
    D -->|Compile Model|> E[Deployment]
    E -->|Deploy Model|> F[Inference]
```
Caption: Overview of the Quantization Process in QEfficient.

## References
- `QEfficient/transformers/quantizers/gptq.py`
- `QEfficient/transformers/models/modeling_auto.py`
- `QEfficient/transformers/quantizers/auto.py`