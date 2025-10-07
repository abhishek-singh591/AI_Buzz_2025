# Introduction to Efficient Transformers
The Efficient Transformers library is designed to improve the efficiency and performance of transformer models, with a focus on large-scale language models and vision-language models. It provides support for various transformer models, including Llama4, Gemma3, and HP-CAI Grok-1, among others.

## Overview
The library enables efficient inference and compilation of these models, with features such as sentence embedding, flexible pooling configuration, and support for multiple sequence lengths. It also supports various model execution modes, including QNN compilation, SwiftKV, and gradient checkpointing.

## Key Components / Concepts
The library consists of several key components, including:
* `QEFFAutoModel`: a class for manipulating any transformer model from the Hugging Face hub
* `QEFFTransformersBase`: a parent class for models provided by QEFF
* `transform_lm`: a function that replaces certain layers in a PyTorch model with optimized modules for Cloud AI 100

## How it Works
The library works by optimizing the transformer models for Cloud AI 100, replacing the torch.nn.Module layers with optimized implementations. It also provides a `from_pretrained` method to load pre-trained models and a `compile` method to compile the model for efficient inference.

## Example(s)
An example of using the library is as follows:
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Initialize the model using from_pretrained
model = QEFFAutoModel.from_pretrained("model_name")

# Compile the model for Cloud AI 100
model.compile(num_cores=16)

# Prepare input
tokenizer = AutoTokenizer.from_pretrained(model_name)
inputs = tokenizer("My name is", return_tensors="pt")

# Execute the model
model.generate(inputs)
```

## Diagram(s)
```mermaid
flowchart LR
    A[Load Pre-trained Model] --> B[Compile Model]
    B --> C[Prepare Input]
    C --> D[Execute Model]
    D --> E[Get Output]
```
The diagram shows the workflow of using the Efficient Transformers library, from loading a pre-trained model to executing the model and getting the output.

## References
* [README.md](README.md)
* [QEfficient/transformers/models/modeling_auto.py](QEfficient/transformers/models/modeling_auto.py)
* [QEfficient/transformers/transform.py](QEfficient/transformers/transform.py)
* [pyproject.toml](pyproject.toml)