# Notebook Helper Functions
## Overview
The `notebooks` package in the `quic/efficient-transformers` repository provides a set of utility functions to simplify the process of loading models, tokenizing input, and visualizing results. These helper functions are designed to make it easier to work with the QEfficient library and to facilitate the development of custom notebooks.

## Key Components / Concepts
The notebook helper functions are built around several key components, including:

* Model loading: The `QEFFCommonLoader` class provides a unified interface for loading Hugging Face models, making it easy to switch between different models and configurations.
* Tokenization: The `load_hf_tokenizer` function loads a pre-trained tokenizer from the Hugging Face model hub, allowing for easy tokenization of input text.
* Result visualization: The `cloud_ai_100_exec_kv` function generates output by executing a compiled model on Cloud AI 100 hardware, providing a convenient way to visualize the results of model inference.

## How it Works
The notebook helper functions work by providing a set of pre-built functions that can be used to perform common tasks, such as loading models, tokenizing input, and visualizing results. These functions are designed to be easy to use and to require minimal configuration, making it easy to get started with the QEfficient library.

For example, the `load_hf_tokenizer` function can be used to load a pre-trained tokenizer from the Hugging Face model hub, like this:
```python
tokenizer = load_hf_tokenizer("gpt2")
```
Similarly, the `cloud_ai_100_exec_kv` function can be used to generate output by executing a compiled model on Cloud AI 100 hardware, like this:
```python
output = cloud_ai_100_exec_kv(tokenizer, "path/to/compiled/model")
```
## Example(s)
Here is an example of how the notebook helper functions can be used to load a model, tokenize some input text, and visualize the results:
```python
# Load the model and tokenizer
model = QEFFCommonLoader.from_pretrained("gpt2")
tokenizer = load_hf_tokenizer("gpt2")

# Tokenize some input text
input_text = "Hello, world!"
inputs = tokenizer(input_text, return_tensors="pt")

# Generate output using the model
output = model.generate(inputs)

# Visualize the results
output = cloud_ai_100_exec_kv(tokenizer, "path/to/compiled/model")
```
## Diagram(s)
```mermaid
flowchart LR
    A[Load Model] -->|model|> B[Tokenize Input]
    B -->|inputs|> C[Generate Output]
    C -->|output|> D[Visualize Results]
```
This flowchart shows the basic workflow of the notebook helper functions, from loading the model to visualizing the results.

## References
* `QEfficient/transformers/models/modeling_auto.py`
* `QEfficient/utils/_utils.py`
* `notebooks/__init__.py`
* `notebooks/QEfficientGPT2.ipynb`