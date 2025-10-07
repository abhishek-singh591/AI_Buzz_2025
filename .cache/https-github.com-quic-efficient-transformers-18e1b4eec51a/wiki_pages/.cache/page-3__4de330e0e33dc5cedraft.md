# Notebooks Overview
## Overview
The notebooks in the QEfficient repository provide a comprehensive overview of the model optimization, export, and inference workflows. These notebooks demonstrate how to onboard large language models (LLMs) on the Cloud AI 100 platform, optimize them for better performance, and execute them for text generation tasks. The notebooks cover various aspects, including model compilation, export to ONNX, and execution on Cloud AI 100 hardware.

## Key Components / Concepts
The key components and concepts used in these notebooks include:
* Model optimization techniques, such as RMS norm fixes and causal mask fixes
* Model export to ONNX format
* Compilation of ONNX models for Cloud AI 100 hardware
* Execution of compiled models on Cloud AI 100 hardware
* Text generation using the executed models

## How it Works
The notebooks work by first downloading and modifying the LLMs using optimized software libraries. The modified models are then exported to the ONNX framework and compiled for the Cloud AI 100 platform. The compiled models are executed on the Cloud AI 100 hardware, and the output is printed to the console. The notebooks also demonstrate how to use the `cloud_ai_100_exec_kv` function to generate output by executing a compiled model on Cloud AI 100 hardware.

## Example(s)
For example, the `QEfficientMPT.ipynb` notebook demonstrates the onboarding of the LLM MPT model on the Cloud AI 100 platform. It takes a HuggingFace model name as input, downloads and modifies the model using optimized software libraries, and generates an optimized model for the Cloud AI 100 platform. The notebook then exports the optimized model to the ONNX framework, compiles it for the Cloud AI 100 platform, and executes it to print latency statistics.

## Diagram(s)
```mermaid
flowchart LR
    A[Download and Modify Model] --> B[Export to ONNX]
    B --> C[Compile for Cloud AI 100]
    C --> D[Execute on Cloud AI 100]
    D --> E[Print Output]
```
This flowchart illustrates the workflow of the notebooks, from downloading and modifying the model to executing it on Cloud AI 100 hardware and printing the output.

## References
* `notebooks/QEfficientMPT.ipynb`: Demonstrates the onboarding of the LLM MPT model on the Cloud AI 100 platform.
* `QEfficient/utils/run_utils.py`: Contains the `run_kv_model_on_cloud_ai_100` function, which runs an ONNX model on Cloud AI 100 for semantic search.
* `QEfficient/generation/text_generation_inference.py`: Contains the `cloud_ai_100_exec_kv` function, which generates output by executing a compiled model on Cloud AI 100 hardware.
* `docs/source/blogs.md`: Provides links to blog posts related to Qualcomm Cloud AI 100, including information on training and inference capabilities, performance optimization, and power-efficient acceleration for large language models.