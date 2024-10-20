import numpy as np


class Layer:

    def __init__(self, input_dim: int, size: int, activation_method: str):
        self.activation_method = activation_method
        self.weights = np.zeros((size, input_dim))
        self.biases = np.zeros((size, 1))

    def randomize_params(self, network_update_variance):
        weights_change = network_update_variance * np.random.randn(self.weights.shape[0], self.weights.shape[1])

        static_ratio = 0.5
        num_elements = weights_change.size
        num_zeros = int(static_ratio * num_elements)
        static_indices = np.random.choice(num_elements, num_zeros, replace=False)
        weights_change.flat[static_indices] = 0

        self.weights += weights_change

        num_elements = weights_change.size
        num_zeros = int(static_ratio * num_elements)
        static_indices = np.random.choice(num_elements, num_zeros, replace=False)
        weights_change.flat[static_indices] = 0

        biases_change = network_update_variance * np.random.randn(self.biases.shape[0], 1)

        num_elements = biases_change.size
        num_zeros = int(static_ratio * num_elements)
        static_indices = np.random.choice(num_elements, num_zeros, replace=False)
        biases_change.flat[static_indices] = 0

        self.biases += biases_change

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
