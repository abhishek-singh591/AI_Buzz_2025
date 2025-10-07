# Project Overview
## Overview
The Efficient Transformers library is a software library designed to optimize large language models (LLMs) for deployment on Qualcomm Cloud AI 100, enabling efficient inference and training. The library provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models from the HuggingFace hub on Cloud AI 100 hardware.

## Key Components / Concepts
The library consists of several key components, including:
* QEFFAutoModel: a class that provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models from the HuggingFace hub on Cloud AI 100 hardware.
* QEFFTransformersBase: a base class for QEfficient wrappers around HuggingFace transformer models, providing common functionality for loading, representing, and managing HuggingFace models within the QEfficient framework.
* from_pretrained: a function that loads a QEfficient transformer model from a pretrained HuggingFace model or local path, initializing it with the pretrained weights.

## How it Works
The library works by taking a model card from HuggingFace or a local model path as input and outputting an optimized model implementation for Cloud AI 100. The library provides reimplemented transformer blocks, graph transformations, and patcher modules to ensure efficient execution and handle precision issues.

## Example(s)
An example of using the QEFFAutoModel class is as follows:
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
    A[HuggingFace Model] -->|from_pretrained|> B[QEFFAutoModel]
    B -->|compile|> C[Optimized Model]
    C -->|generate|> D[Output]
```
Caption: Overview of the QEFFAutoModel class and its usage.

## References
* [README.md](README.md)
* [docs/index.rst](docs/index.rst)
* [QEfficient/transformers/models/modeling_auto.py](QEfficient/transformers/models/modeling_auto.py)
* [docs/source/quick_start.md](docs/source/quick_start.md)
* [docs/source/release_docs.md](docs/source/release_docs.md)