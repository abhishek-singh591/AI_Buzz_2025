# Training and Labeling Functions
## Overview
The EIGEN project utilizes various training and labeling functions to achieve high-fidelity information extraction from document images. The main functions are implemented in the `main.py` and `train.py` files.

## Key Components / Concepts
The key components of the training and labeling functions include:
* The `JL` class, which represents a joint learning model that combines feature-based classification and graphical models for classification tasks.
* The `fit_and_predict_proba` function, which trains a model on labeled and unlabeled instances and predicts the probability of each instance belonging to each class.
* The `convert_examples_to_featuresz` function, which converts a list of examples into a format suitable for input to a semantic search model.

## How it Works
The training and labeling functions work as follows:
1. The `CORD_train` function processes raw labeled data from the CORD dataset, extracting text, bounding boxes, and labels from annotated medical documents.
2. The `convert_examples_to_featuresz` function converts the extracted data into a format suitable for input to a semantic search model.
3. The `JL` class is initialized with the converted data and trained using various loss functions.
4. The `fit_and_predict_proba` function is used to train the model and predict the probability of each instance belonging to each class.

## Example(s)
An example of how to use the `CORD_train` function is as follows:
```python
directory = 'CORD/train/json'
words, bbox, labels = CORD_train(directory)
```
This code processes the raw labeled data from the CORD dataset and extracts the text, bounding boxes, and labels.

## Diagram(s)
```mermaid
flowchart LR
    A[CORD Dataset] -->|Processed by|> B[CORD_train]
    B -->|Extracts|> C[Text, Bounding Boxes, Labels]
    C -->|Converted by|> D[convert_examples_to_featuresz]
    D -->|Trained by|> E[JL Class]
    E -->|Predicts|> F[Probability of each instance]
```
This flowchart illustrates the process of training and labeling in the EIGEN project.

## References
* `main.py`
* `train.py`
* `README.md`
* `train_copy.py`