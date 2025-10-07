# Introduction to Efficient Transformers
The Efficient Transformers Library is a library that provides support for various transformer models, including Llama4, Gemma3, and HP-CAI Grok-1, among others. It enables efficient inference and compilation of these models, with features such as sentence embedding, flexible pooling configuration, and support for multiple sequence lengths.

## Overview
The library supports various model execution modes, including QNN compilation, SwiftKV, and gradient checkpointing, and has added support for new models and features in recent updates. The library is designed to improve the efficiency and performance of transformer models, with a focus on large-scale language models and vision-language models.

## Key Components / Concepts
The library includes several key components, such as the QEFFAutoModel class, which is designed for manipulating any transformer model from the HuggingFace hub. The class provides a `from_pretrained` method to load pre-trained models and can be compiled for Cloud AI 100.

## How it Works
The library optimizes models for Cloud AI 100 by replacing torch.nn.Module layers with optimized implementations. The `transform` function takes a QEFFBaseModel object and a form factor configuration as inputs and modifies the input model object in place.

## Example(s)
An example of using the library is to initialize a QEFFAutoModelForCausalLM model using the `from_pretrained` method and then compile it for Cloud AI 100 using the `compile` method.

## Diagram(s)
```mermaid
flowchart LR
    A[Model Initialization] --> B[Model Compilation]
    B --> C[Model Execution]
    C --> D[Output Generation]
```
This flowchart shows the basic workflow of the Efficient Transformers Library, from model initialization to output generation.

## References
* [README.md](README.md)
* [QEfficient/transformers/models/modeling_auto.py](QEfficient/transformers/models/modeling_auto.py)
* [QEfficient/transformers/transform.py](QEfficient/transformers/transform.py)
* [QEfficient/peft/pytorch_transforms.py](QEfficient/peft/pytorch_transforms.py)