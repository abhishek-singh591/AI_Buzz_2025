# Finetuning Examples
## Overview
Finetuning is a crucial step in adapting pre-trained models to specific tasks or datasets. QEfficient provides an efficient way to fine-tune models using its `QEFFAutoModel` class.

## Key Components / Concepts
The key components involved in finetuning with QEfficient are:
- `QEFFAutoModel`: The class used for manipulating transformer models from the HuggingFace hub.
- `from_pretrained`: A method that initializes a QEfficient model from a pre-trained model.

## How it Works
To fine-tune a model, you first initialize it using the `from_pretrained` method, specifying the model name or path. Then, you can compile the model for your specific task or device.

## Example(s)
Here's an example of how to initialize and compile a model:
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Initialize the model
model = QEFFAutoModel.from_pretrained("model_name")

# Compile the model for Cloud AI 100
model.compile(num_cores=16)

# Prepare input
tokenizer = AutoTokenizer.from_pretrained("model_name")
inputs = tokenizer("My name is", return_tensors="pt")

# Execute the model
model.generate(inputs)
```

## Diagram(s)
```mermaid
flowchart LR
    A[Load Pre-trained Model] -->|using from_pretrained|> B[Initialize QEFFAutoModel]
    B -->|compile|> C[Compile Model for Task/Device]
    C -->|generate/input|> D[Execute Model]
```
Caption: Finetuning Workflow with QEfficient

## References
- `QEfficient/transformers/models/modeling_auto.py`
- `tests/finetune/test_finetune.py`
- `QEfficient/finetune/eval.py`
- `QEfficient/finetune/utils/config_utils.py`