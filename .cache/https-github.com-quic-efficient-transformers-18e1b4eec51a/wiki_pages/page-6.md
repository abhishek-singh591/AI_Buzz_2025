# Core Architectural Components
## Overview
The core architectural components of the QEfficient library are designed to optimize large language models (LLMs) for deployment on Qualcomm Cloud AI 100, enabling efficient inference and training. The library takes a model card from HuggingFace or a local model path as input and outputs an optimized model implementation for Cloud AI 100. This optimization process involves a series of transformations and modifications to the original model architecture, allowing it to leverage the capabilities of the Cloud AI 100 hardware.

The QEfficient library is built on top of the HuggingFace Transformers library, which provides a wide range of pre-trained models and a unified interface for loading, exporting, and running these models. By extending the HuggingFace library, QEfficient is able to support a variety of model architectures and provide a seamless integration with the Cloud AI 100 platform.

## Key Components / Concepts
The key components of the QEfficient library include:
* **Reimplemented transformer blocks**: These blocks are designed to enable efficient on-device retention of intermediate states, reducing the memory footprint and improving the overall performance of the model.
* **Graph transformations**: These transformations enable the execution of key operations in lower precision, which can significantly reduce the computational requirements and improve the efficiency of the model.
* **Graph transformations to replace operations**: Some operations in the original model are replaced with mathematically equivalent operations that are more efficient or better supported on the Cloud AI 100 hardware.
* **Handling for underflow and overflows**: The library includes mechanisms to handle underflow and overflows that may occur when operating in lower precision, ensuring the stability and accuracy of the model.
* **Patcher modules**: These modules are used to manage precision issues and ensure that the model operates correctly even in situations where the precision of the input data may be limited.

## How it Works
The QEfficient library works by optimizing a given model for Cloud AI 100 through the `transform` function, which replaces the torch.nn.Module layers of the passed QEffModel with optimized implementations. The `QEFFAutoModel` class provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models on Cloud AI 100 hardware.

The optimization process involves several steps:
1. **Model loading**: The original model is loaded from a model card or a local path.
2. **Model analysis**: The library analyzes the model architecture and identifies opportunities for optimization.
3. **Transformation**: The library applies the necessary transformations to the model, including the implementation of efficient transformer blocks, graph transformations, and the replacement of operations.
4. **Compilation**: The optimized model is compiled for execution on the Cloud AI 100 hardware.
5. **Execution**: The optimized model is executed on the Cloud AI 100 hardware, performing inference or training as required.

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
This example demonstrates how to load a pre-trained model, compile it for execution on the Cloud AI 100 hardware, and perform inference using the optimized model.

## Diagram(s)
```mermaid
flowchart LR
    A[Model Input] -->|Model Card or Local Path|> B(QEfficient Library)
    B -->|Optimized Model|> C[Cloud AI 100]
    C -->|Inference/Training|> D[Output]
    B -->|Model Analysis|> E[Transformation]
    E -->|Optimized Model|> B
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style E fill:#ccc,stroke:#333,stroke-width:4px
```
The diagram illustrates the high-level workflow of the QEfficient library, where a model input is passed to the library, which optimizes the model for Cloud AI 100 and then performs inference or training to produce the output. The diagram also highlights the key components of the library, including the model analysis and transformation steps.

## References
* `QEfficient/transformers/models/modeling_auto.py`
* `QEfficient/transformers/transform.py`
* `docs/source/introduction.md`
* `tests/transformers/models/test_causal_lm_models.py`