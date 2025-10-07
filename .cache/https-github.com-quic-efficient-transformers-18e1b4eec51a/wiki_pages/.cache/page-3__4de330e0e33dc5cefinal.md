# Notebooks Overview
## Overview
The notebooks in the QEfficient repository provide a comprehensive overview of the model optimization, export, and inference workflows. These notebooks demonstrate how to onboard large language models (LLMs) on the Cloud AI 100 platform, optimize them for better performance, and execute them for text generation tasks. The notebooks cover various aspects, including model compilation, export to ONNX, and execution on Cloud AI 100 hardware. This documentation will delve into the details of these notebooks, providing a thorough understanding of the concepts, components, and workflows involved.

The QEfficient repository is designed to facilitate the optimization and deployment of LLMs on the Cloud AI 100 platform. The notebooks serve as a guide, walking users through the process of onboarding, optimizing, and executing these models. By following the workflows outlined in the notebooks, users can leverage the capabilities of the Cloud AI 100 platform to improve the performance and efficiency of their LLMs.

## Key Components / Concepts
The key components and concepts used in these notebooks include:
* Model optimization techniques, such as RMS norm fixes and causal mask fixes, which are essential for improving the performance and stability of LLMs.
* Model export to ONNX format, which enables the deployment of LLMs on a variety of platforms, including the Cloud AI 100.
* Compilation of ONNX models for Cloud AI 100 hardware, which involves optimizing the model for the specific hardware architecture to achieve optimal performance.
* Execution of compiled models on Cloud AI 100 hardware, which allows users to leverage the capabilities of the platform to generate text and perform other tasks.
* Text generation using the executed models, which demonstrates the practical application of the optimized LLMs.

These components and concepts are crucial to the workflows outlined in the notebooks. By understanding how to optimize, export, and execute LLMs, users can unlock the full potential of the Cloud AI 100 platform and achieve significant improvements in performance and efficiency.

## How it Works
The notebooks work by first downloading and modifying the LLMs using optimized software libraries. This involves applying techniques such as RMS norm fixes and causal mask fixes to improve the stability and performance of the models. The modified models are then exported to the ONNX framework, which provides a standardized format for deploying models on a variety of platforms.

Once the models are exported to ONNX, they are compiled for the Cloud AI 100 platform. This involves optimizing the model for the specific hardware architecture, which enables the model to achieve optimal performance. The compiled models are then executed on the Cloud AI 100 hardware, which allows users to generate text and perform other tasks.

The notebooks also demonstrate how to use the `cloud_ai_100_exec_kv` function to generate output by executing a compiled model on Cloud AI 100 hardware. This function provides a convenient interface for executing models and generating output, making it easier for users to leverage the capabilities of the platform.

## Example(s)
For example, the `QEfficientMPT.ipynb` notebook demonstrates the onboarding of the LLM MPT model on the Cloud AI 100 platform. It takes a HuggingFace model name as input, downloads and modifies the model using optimized software libraries, and generates an optimized model for the Cloud AI 100 platform. The notebook then exports the optimized model to the ONNX framework, compiles it for the Cloud AI 100 platform, and executes it to print latency statistics.

This example illustrates the workflow outlined in the notebooks, from downloading and modifying the model to executing it on Cloud AI 100 hardware and printing the output. By following this workflow, users can optimize and deploy their own LLMs on the Cloud AI 100 platform, achieving significant improvements in performance and efficiency.

Another example is the `QEfficient/utils/run_utils.py` notebook, which contains the `run_kv_model_on_cloud_ai_100` function. This function runs an ONNX model on Cloud AI 100 for semantic search, demonstrating the practical application of the optimized LLMs. By using this function, users can execute their own models on the Cloud AI 100 platform, leveraging the capabilities of the platform to generate text and perform other tasks.

## Diagram(s)
```mermaid
flowchart LR
    A[Download and Modify Model] --> B[Export to ONNX]
    B --> C[Compile for Cloud AI 100]
    C --> D[Execute on Cloud AI 100]
    D --> E[Print Output]
    E --> F[Generate Text]
    F --> G[Perform Semantic Search]
```
This flowchart illustrates the workflow of the notebooks, from downloading and modifying the model to executing it on Cloud AI 100 hardware and printing the output. The additional steps of generating text and performing semantic search demonstrate the practical application of the optimized LLMs.

## References
* `notebooks/QEfficientMPT.ipynb`: Demonstrates the onboarding of the LLM MPT model on the Cloud AI 100 platform.
* `QEfficient/utils/run_utils.py`: Contains the `run_kv_model_on_cloud_ai_100` function, which runs an ONNX model on Cloud AI 100 for semantic search.
* `QEfficient/generation/text_generation_inference.py`: Contains the `cloud_ai_100_exec_kv` function, which generates output by executing a compiled model on Cloud AI 100 hardware.
* `docs/source/blogs.md`: Provides links to blog posts related to Qualcomm Cloud AI 100, including information on training and inference capabilities, performance optimization, and power-efficient acceleration for large language models.
* `QEfficient/README.md`: Provides an overview of the QEfficient repository, including information on the notebooks, models, and workflows involved.