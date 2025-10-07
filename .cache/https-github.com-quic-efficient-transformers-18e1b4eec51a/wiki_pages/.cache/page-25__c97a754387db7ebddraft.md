# Quick Start Example
The Efficient Transformers library provides support for various transformer models, including Llama4, Gemma3, and HP-CAI Grok-1, among others. This quick start example demonstrates how to get started with the library.

## Overview
The library enables efficient inference and compilation of transformer models, with features such as sentence embedding, flexible pooling configuration, and support for multiple sequence lengths.

## Key Components / Concepts
* `QEFFAutoModel`: A class for manipulating transformer models from the Hugging Face hub.
* `from_pretrained`: A method for initializing a QEfficient model from a pre-trained model.
* `compile`: A method for compiling a model for Cloud AI 100.

## How it Works
1. Initialize a QEfficient model using the `from_pretrained` method.
2. Compile the model for Cloud AI 100 using the `compile` method.
3. Prepare input data using a tokenizer.
4. Execute the model using the `generate` method.

## Example(s)
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Initialize the model using from_pretrained
model = QEFFAutoModel.from_pretrained("model_name")

# Compile the model for Cloud AI 100
model.compile(num_cores=16)

# Prepare input data
tokenizer = AutoTokenizer.from_pretrained("model_name")
inputs = tokenizer("My name is", return_tensors="pt")

# Execute the model
output = model.generate(inputs)
```

## Diagram(s)
```mermaid
flowchart LR
    A[Initialize Model] --> B[Compile Model]
    B --> C[Prepare Input]
    C --> D[Execute Model]
    D --> E[Get Output]
```
Caption: Quick Start Example Flowchart

## References
* [README.md](README.md)
* [QEfficient/transformers/models/modeling_auto.py](QEfficient/transformers/models/modeling_auto.py)
* [tests/transformers/test_transformer_pytorch_transforms.py](tests/transformers/test_transformer_pytorch_transforms.py)
* [QEfficient/transformers/models/llama4/modeling_llama4.py](QEfficient/transformers/models/llama4/modeling_llama4.py)
* [examples/draft_spd_inference.py](examples/draft_spd_inference.py)