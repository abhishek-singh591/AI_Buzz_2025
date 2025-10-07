# Core Architectural Components
## Overview
The core architectural components of the QEfficient library are designed to optimize large language models (LLMs) for deployment on Qualcomm Cloud AI 100, enabling efficient inference and training. The library takes a model card from HuggingFace or a local model path as input and outputs an optimized model implementation for Cloud AI 100.

## Key Components / Concepts
The key components of the QEfficient library include:
* Reimplemented transformer blocks to enable efficient on-device retention of intermediate states
* Graph transformations to enable execution of key operations in lower precision
* Graph transformations to replace some operations with other mathematically equivalent operations that are efficient/supported on HW backend
* Handling for underflow and overflows in lower precision
* Patcher modules to manage precision issues

## How it Works
The QEfficient library works by optimizing a given model for Cloud AI 100 through the `transform` function, which replaces the torch.nn.Module layers of the passed QEffModel with optimized implementations. The `QEFFAutoModel` class provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models on Cloud AI 100 hardware.

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
    A[Model Input] -->|Model Card or Local Path|> B(QEfficient Library)
    B -->|Optimized Model|> C[Cloud AI 100]
    C -->|Inference/Training|> D[Output]
```
The diagram illustrates the high-level workflow of the QEfficient library, where a model input is passed to the library, which optimizes the model for Cloud AI 100 and then performs inference or training to produce the output.

## References
* `QEfficient/transformers/models/modeling_auto.py`
* `QEfficient/transformers/transform.py`
* `docs/source/introduction.md`
* `tests/transformers/models/test_causal_lm_models.py`
* `QEfficient/peft/lora/auto.py`