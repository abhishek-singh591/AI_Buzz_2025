# System Architecture
## Overview
The QEfficient library is designed to simplify the onboarding of models inference for any Transformer architecture on Cloud AI platforms. It provides a layered architecture consisting of a base model class, transformer transforms, and a QNN compilation pipeline. This architecture enables efficient model optimization, compilation, and deployment on Cloud AI 100 hardware.

## Key Components / Concepts
The key components of the QEfficient library include:
* **Base Model Class**: The `QEFFBaseModel` class serves as the foundation for various model classes, providing utility methods for tasks such as applying PyTorch and ONNX transformations.
* **Transformer Transforms**: The `transform` function optimizes a given model for Cloud AI 100 by replacing its `torch.nn.Module` layers with optimized implementations.
* **QNN Compilation Pipeline**: The `compile` function compiles a given ONNX model using the QNN compiler and saves the compiled `qpc` package.

## How it Works
The QEfficient library works by first applying PyTorch transformations to the input model, followed by ONNX transformations after exporting the model to ONNX format. The transformed model is then compiled using the QNN compiler, resulting in a compiled `qpc` package that can be deployed on Cloud AI 100 hardware.

## Example(s)
An example of using the QEfficient library is as follows:
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

model = QEFFAutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2", pooling="mean")
model.compile(num_cores=16)
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
inputs = tokenizer("My name is", return_tensors="pt")
output = model.generate(inputs)
print(output)  # Output will be a dictionary containing extracted features.
```
## Diagram(s)
```mermaid
flowchart LR
    A[Input Model] -->|Apply PyTorch Transforms|> B[Transformed Model]
    B -->|Export to ONNX|> C[ONNX Model]
    C -->|Apply ONNX Transforms|> D[Transformed ONNX Model]
    D -->|Compile with QNN|> E[Compiled QPC Package]
    E -->|Deploy on Cloud AI 100|> F[Deployed Model]
```
Caption: QEfficient Library Workflow

## References
* `QEfficient/base/modeling_qeff.py`: Base model class implementation
* `QEfficient/compile/qnn_compiler.py`: QNN compilation pipeline implementation
* `QEfficient/transformers/transform.py`: Transformer transforms implementation
* `tests/transformers/models/test_causal_lm_models.py`: Example usage of QEfficient library for causal language models
* `docs/source/finetune.md`: Finetuning infrastructure documentation