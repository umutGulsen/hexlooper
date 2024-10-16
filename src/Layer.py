import numpy as np


class Layer:

    def __init__(self, input_dim: int, size: int, activation_method: str):
        self.activation_method = activation_method
        self.weights = np.zeros((size, input_dim))
        self.biases = np.zeros((size, 1))

    def randomize_params(self, network_update_variance):
        self.weights += network_update_variance * np.random.randn(self.weights.shape[0], self.weights.shape[1])
        self.biases += network_update_variance * np.random.randn(self.biases.shape[0], 1)

    def activation(self, x):
        if self.activation_method == "relu":
            return np.maximum(0, x)
        else:
            return x

    def forward_prop(self, x_input: np.ndarray):
        output = np.dot(self.weights, x_input)
        output += self.biases
        output = self.activation(output)
        return output
