# Library Overview
## Overview
The Efficient Transformers library is a Python package designed to optimize large language models (LLMs) for deployment on Qualcomm Cloud AI 100, enabling efficient inference and training. The library provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models from the HuggingFace hub on Cloud AI 100 hardware. This optimization is crucial for real-world applications where computational resources are limited, and efficient model deployment is essential for achieving desired performance metrics.

The library's primary goal is to bridge the gap between the HuggingFace ecosystem and Qualcomm Cloud AI 100 hardware, allowing developers to leverage the strengths of both worlds. By providing an optimized implementation of transformer models, the library enables faster inference times, reduced memory usage, and improved overall system performance. This is particularly important for applications that require low latency and high throughput, such as natural language processing, sentiment analysis, and text classification.

## Key Components / Concepts
The library consists of several key components, including:
* `QEFFTransformersBase`: a base class for QEfficient wrappers around HuggingFace transformer models, providing common functionality for loading, representing, and managing these models. This base class serves as the foundation for all QEfficient transformer models, ensuring consistency and interoperability across different model implementations.
* `QEFFAutoModel`: a class that provides a unified interface for loading, exporting, compiling, and running various encoder-only transformer models on Cloud AI 100 hardware. This class is the primary entry point for users, allowing them to easily work with different transformer models and optimize them for their specific use cases.
* `from_pretrained`: a function that loads a QEfficient transformer model from a pretrained HuggingFace model or local path, initializing it with the pretrained weights. This function enables users to leverage the vast repository of pretrained models available in the HuggingFace ecosystem and fine-tune them for their specific tasks.

In addition to these core components, the library also provides a range of utility functions and classes that facilitate model optimization, compilation, and deployment. These include tools for model pruning, quantization, and knowledge distillation, which can be used to further optimize model performance and reduce computational requirements.

## How it Works
The library works by taking a model card from HuggingFace or a local model path as input and outputting an optimized model implementation for Cloud AI 100. The library provides reimplemented transformer blocks, graph transformations, and patcher modules to ensure efficient execution and handle precision issues. This process involves several key steps:

1. **Model Loading**: The library loads the specified model from HuggingFace or a local path, using the `from_pretrained` function to initialize the model with pretrained weights.
2. **Model Optimization**: The library applies a range of optimization techniques to the loaded model, including model pruning, quantization, and knowledge distillation. These techniques are designed to reduce computational requirements and improve model performance.
3. **Model Compilation**: The optimized model is then compiled for deployment on Cloud AI 100 hardware, using the `compile` method to generate an optimized model implementation.
4. **Model Deployment**: The compiled model is deployed on Cloud AI 100 hardware, where it can be used for inference and training tasks.

The library's optimization process is designed to be flexible and customizable, allowing users to tailor the optimization process to their specific use cases and requirements. This includes support for different optimization techniques, model architectures, and hardware configurations.

## Example(s)
Here is an example of how to use the `QEFFAutoModel` class:
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
This example demonstrates how to load a pretrained model, compile it for deployment on Cloud AI 100, and use it for inference tasks. The `QEFFAutoModel` class provides a simple and intuitive interface for working with transformer models, making it easy to optimize and deploy models for a range of applications.

In addition to this example, the library also provides a range of other examples and tutorials that demonstrate how to use the library for different tasks and applications. These include examples of how to use the library for text classification, sentiment analysis, and question answering, as well as tutorials on how to optimize and deploy models for specific use cases.

## Diagram(s)
```mermaid
flowchart LR
    A[HuggingFace Model] -->|from_pretrained|> B[QEFFAutoModel]
    B -->|compile|> C[Compiled Model]
    C -->|generate|> D[Output]
    D -->|post-processing|> E[Final Output]
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#f9f,stroke:#333,stroke-width:4px
    style C fill:#f9f,stroke:#333,stroke-width:4px
    style D fill:#f9f,stroke:#333,stroke-width:4px
    style E fill:#f9f,stroke:#333,stroke-width:4px
```
Caption: Overview of the Efficient Transformers library workflow.

This diagram provides a high-level overview of the library's workflow, from model loading and optimization to deployment and inference. The diagram highlights the key components and steps involved in the library's workflow, making it easy to understand how the library works and how to use it for different applications.

## References
* [README.md](README.md)
* [docs/source/release_docs.md](docs/source/release_docs.md)
* [QEfficient/transformers/models/modeling_auto.py](QEfficient/transformers/models/modeling_auto.py)
* [docs/source/supported_features.rst](docs/source/supported_features.rst)
* [docs/source/quick_start.md](docs/source/quick_start.md)