# Modeling Utilities
## Overview
The QEfficient library provides a range of modeling utilities to support the development and deployment of transformer-based models. These utilities include classes and functions for manipulating models, compiling models for deployment on specific hardware, and optimizing model performance.

## Key Components / Concepts
The key components of the modeling utilities include:
* `QEFFAutoModel`: a class for manipulating transformer models from the Hugging Face hub
* `modeling_utils.py`: a module providing utility functions and classes for modeling and building transformer-based models
* `QEffLlama4VisionRotaryEmbedding`: a class for initializing rotary embeddings in QEff models

## How it Works
The modeling utilities work by providing a set of classes and functions that can be used to manipulate and optimize transformer-based models. For example, the `QEFFAutoModel` class can be used to initialize a model from a Hugging Face model hub, and then compile it for deployment on a specific hardware platform.

## Example(s)
```python
from QEfficient import QEFFAutoModel
from transformers import AutoTokenizer

# Initialize the model using from_pretrained similar to transformers.AutoModel
model = QEFFAutoModel.from_pretrained("model_name")

# Now you can directly compile the model for Cloud AI 100
model.compile(num_cores=16)  # Considering you have a Cloud AI 100 SKU

# Prepare input
tokenizer = AutoTokenizer.from_pretrained(model_name)
inputs = tokenizer("My name is", return_tensors="pt")

# You can now execute the model
model.generate(inputs)
```

## Diagram(s)
```mermaid
flowchart LR
    A[Model Initialization] -->|from_pretrained|> B[QEFFAutoModel]
    B -->|compile|> C[Compiled Model]
    C -->|generate|> D[Model Output]
```
Modeling Utilities Flowchart

## References
* `QEfficient/transformers/models/modeling_auto.py`
* `QEfficient/transformers/modeling_utils.py`
* `tests/transformers/models/test_causal_lm_models.py`