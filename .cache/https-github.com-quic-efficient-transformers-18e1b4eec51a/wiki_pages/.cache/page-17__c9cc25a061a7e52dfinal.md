# Speculative Decoding
## Overview
Speculative decoding is a core feature in QEfficient, enabling efficient and accurate language modeling by generating text based on a given prompt while considering potential future tokens.

## Key Components / Concepts
The speculative decoding process involves several key components, including:
* **SpDTransform**: A class that applies a transformation to a PyTorch model to support speculative decoding, as defined in `QEfficient/transformers/models/pytorch_transforms.py`.
* **QEffLlama4DecoderWrapper**: A decoder wrapper for the Llama4 model, used in speculative decoding and implemented in `QEfficient/transformers/models/llama4/modeling_llama4.py`.
* **QEffGemma3DecoderWrapper**: A decoder wrapper for the Gemma3 model, used in speculative decoding.

## How it Works
The speculative decoding process works as follows:
1. The input prompt is tokenized and passed through the model.
2. The model generates a set of potential future tokens, based on the input prompt.
3. The model then uses these potential future tokens to inform its generation of the next token.

## Example(s)
An example of speculative decoding can be seen in the `tests/transformers/spd/test_pld_inference.py` file, which tests the speculative decoding inference on a list of prompts using a target model.

## Diagram(s)
```mermaid
flowchart
    A[Input Prompt] -->|Tokenized|> B[Model]
    B --> C[Generate Potential Future Tokens]
    C --> D[Inform Next Token Generation]
    D --> E[Output Token]
```
Caption: Speculative Decoding Process

## References
* `tests/transformers/spd/test_pld_inference.py`
* `QEfficient/transformers/models/pytorch_transforms.py`
* `QEfficient/transformers/models/llama4/modeling_llama4.py`
* `QEfficient/transformers/models/gemma3/modeling_gemma3.py`