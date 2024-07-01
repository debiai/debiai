from backend.modules.algoProviders.integratedAlgoProvider.utils import (
    get_input_from_inputs,
)

# from ..utils import get_input_from_inputs


# This algorithm is a simple regression metric calculator
# It takes a list of numbers corresponding to an error
# and a ceil corresponding to the maximum acceptable error

# It returns a list of True/False values corresponding to
# whether the error is acceptable or not

# It also returns the percentage of acceptable errors

# Technical details (must respect the algo-api format):
algorithm_description = {
    "name": "Regression Metric",
    "description": """Calculates the regression error according to the ground truth, \
the predictions and a ceil value""",
    "author": "DebiAI",
    "version": "1.0.0",
    "creationDate": "2023-05-23",
    "tags": ["metrics", "regression"],
    "inputs": [
        {
            "name": "Ground truth",
            "description": "List of ground truth values",
            "type": "array",
            "arrayType": "number",
        },
        {
            "name": "Predictions",
            "description": "List of predictions, must have the same length as the  \
ground truth list",
            "type": "array",
            "arrayType": "number",
        },
        {
            "name": "Ceil",
            "description": "Maximum acceptable error, depends on the use case, >= 0",
            "type": "number",
            "default": 5,
            "availableValues": [0.1, 5, 100, 10000],
            "min": 0,
        },
    ],
    "outputs": [
        {
            "name": "Error",
            "description": "Difference between the ground truth and the predictions",
            "type": "array",
            "arrayType": "number",
        },
        {
            "name": "Absolute error",
            "description": "Absolute value of the error",
            "type": "array",
            "arrayType": "number",
        },
        {
            "name": "Binary error",
            "description": "True if Absolute error > ceil, False otherwise",
            "type": "array",
            "arrayType": "boolean",
        },
        {
            "name": "Error percentage",
            "type": "number",
        },
        {
            "name": "Binary success",
            "description": "True if Absolute error <= ceil, False otherwise",
            "type": "array",
            "arrayType": "boolean",
        },
        {
            "name": "Success percentage",
            "type": "number",
        },
    ],
}


def get_algorithm_details():
    return algorithm_description


def use_algorithm(inputs):
    # Get inputs
    gdt = get_input_from_inputs(inputs, "Ground truth", "array", "number")
    predictions = get_input_from_inputs(inputs, "Predictions", "array", "number")
    ceil = get_input_from_inputs(inputs, "Ceil", "number")

    # Check inputs
    if ceil < 0:
        raise TypeError("Ceil must be positive")

    if len(gdt) != len(predictions):
        raise TypeError("Ground truth and predictions must have the same length")

    # Calculate regression metric
    nb_values = len(gdt)
    error = [None] * nb_values
    absolute_error = [None] * nb_values
    binary_error = [None] * nb_values
    binary_success = [None] * nb_values

    for i in range(nb_values):
        error_value = gdt[i] - predictions[i]
        error[i] = error_value
        absolute_error[i] = abs(error_value)

        if abs(error_value) > ceil:
            binary_error[i] = True
            binary_success[i] = False
        else:
            binary_error[i] = False
            binary_success[i] = True

    # Calculate percentages
    error_percentage = binary_error.count(True) / nb_values
    error_percentage = round(error_percentage * 100, 2)
    success_percentage = binary_success.count(True) / nb_values
    success_percentage = round(success_percentage * 100, 2)

    # Return outputs
    return [
        {
            "name": "Error",
            "value": error,
        },
        {
            "name": "Absolute error",
            "value": absolute_error,
        },
        {
            "name": "Binary error",
            "value": binary_error,
        },
        {
            "name": "Error percentage",
            "value": error_percentage,
        },
        {
            "name": "Binary success",
            "value": binary_success,
        },
        {
            "name": "Success percentage",
            "value": success_percentage,
        },
    ]
