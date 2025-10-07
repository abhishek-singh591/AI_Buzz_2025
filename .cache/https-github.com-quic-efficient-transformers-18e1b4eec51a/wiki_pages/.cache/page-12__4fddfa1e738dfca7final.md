# Model Implementations
## Overview
QEfficient provides various model implementations for efficient transformer models, designed to work seamlessly with the Hugging Face transformers library, facilitating easy integration into existing projects.

## Key Components / Concepts
The key components of QEfficient model implementations include:
* `QEFFAutoModel`: a class that manipulates any transformer model from the Hugging Face hub, allowing for easy initialization, compilation, and execution of the model.
* `QEffAutoPeftModelForCausalLM` and `QEffPeftModelForCausalLM`: models specifically designed for causal language modeling tasks.

## How it Works
The QEfficient models operate by applying targeted transforms to the model, including embedding-specific transforms and ONNX transforms. Additionally, they configure the model's cache to True and update the attention implementation and low CPU memory usage settings to optimize performance.

## Example(s)
An example of utilizing the `QEFFAutoModel` class is:
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Initialize the model using from_pretrained similar to transformers.AutoModel.
model = QEFFAutoModel.from_pretrained("model_name")

# Compile the model for Cloud AI 100
model.compile(num_cores=16)  # Considering you have a Cloud AI 100 SKU

# Prepare input
tokenizer = AutoTokenizer.from_pretrained(model_name)
inputs = tokenizer("My name is", return_tensors="pt")

# Execute the model
model.generate(inputs)
```

## Diagram(s)
```mermaid
classDiagram
    class QEFFAutoModel {
        +from_pretrained()
        +compile()
        +generate()
    }
    class QEffAutoPeftModelForCausalLM {
        +from_pretrained()
    }
    class QEffPeftModelForCausalLM {
        +from_pretrained()
    }
    QEFFAutoModel --|> QEffAutoPeftModelForCausalLM
    QEFFAutoModel --|> QEffPeftModelForCausalLM
```
Caption: QEfficient Model Class Diagram

## References
* `tests/transformers/models/test_causal_lm_models.py`
* `QEfficient/transformers/models/modeling_auto.py`
* `tests/peft/test_peft_onnx_transforms.py`
* `QEfficient/transformers/models/llava_next/modeling_llava_next.py`