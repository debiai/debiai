from backend.modules.algoProviders.integratedAlgoProvider.utils import (
    get_input_from_inputs,
)

# from ..utils import get_input_from_inputs

# This algorithm is a simple classification metric calculator
# It takes a list of values corresponding to the ground truth
# and a list of values corresponding to the predictions

# It returns a list of True/False values corresponding to
# whether the prediction is correct or not

# It also returns the accuracy percentage and the number of correct predictions

# Technical details (must respect the algo-api format):
algorithm_description = {
    "name": "Classification Metric",
    "description": """Calculates the classification error according \
to the ground truth and the predictions""",
    "author": "DebiAI",
    "version": "1.0.0",
    "creationDate": "2023-10-30",
    "tags": ["metrics", "classification"],
    "inputs": [
        {
            "name": "Ground truth",
            "description": "List of ground truth values",
            "type": "array",
            "arrayType": "text",
        },
        {
            "name": "Predictions",
            "description": "List of predictions, must have the same \
length as the ground truth list",
            "type": "array",
            "arrayType": "text",
        },
    ],
    "outputs": [
        {
            "name": "Binary error",
            "description": "Classification metric of the input list, \
False if GDT == PRED, True otherwise",
            "type": "array",
            "arrayType": "boolean",
        },
        {
            "name": "Binary success",
            "description": "Classification metric of the input list, \
True if GDT == PRED, False otherwise",
            "type": "array",
            "arrayType": "boolean",
        },
        {
            "name": "Accuracy",
            "description": "Percentage of correct predictions",
            "type": "number",
        },
        {
            "name": "Number of correct predictions",
            "type": "number",
        },
    ],
}


def get_algorithm_details():
    return algorithm_description


def use_algorithm(inputs):
    # Get inputs
    gdt = get_input_from_inputs(inputs, "Ground truth", "array")
    predictions = get_input_from_inputs(inputs, "Predictions", "array")

    # Check inputs
    if len(gdt) != len(predictions):
        raise TypeError("Ground truth and predictions must have the same length")

    # Calculate classification metric
    binary_error = [None] * len(gdt)
    binary_success = [None] * len(gdt)
    nb_correct_predictions = 0
    for i in range(len(gdt)):
        if gdt[i] == predictions[i]:
            nb_correct_predictions += 1
            binary_error[i] = False
            binary_success[i] = True
        else:
            binary_error[i] = True
            binary_success[i] = False

    # Calculate accuracy
    accuracy = nb_correct_predictions / len(binary_success)

    # Return outputs
    return [
        {"name": "Binary error", "value": binary_error},
        {"name": "Binary success", "value": binary_success},
        {"name": "Accuracy", "value": accuracy},
        {"name": "Number of correct predictions", "value": nb_correct_predictions},
    ]
