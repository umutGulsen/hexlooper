import numpy as np


class Layer:

    def __init__(self, input_dim: int, size: int, activation_method: str):
        self.activation_method = activation_method
        self.weights = np.zeros((size, input_dim))
        self.biases = np.zeros((size,1))

    def randomize_params(self):
        self.weights += np.random.randn(self.weights.shape[0], self.weights.shape[1])
        self.biases += 1+np.random.randn(1, self.biases.shape[1])

    def activation(self, x):
        if self.activation_method == "relu":
            return np.maximum(0, x)
        else:
            return x

    def forward_prop(self, x_input: np.ndarray):
        print(f"{x_input.shape=} {self.weights.shape=} {self.biases.shape=}")
        output = np.dot(self.weights, x_input)
        print(f"{x_input.shape=} {self.weights.shape=} {output.shape=} {self.biases.shape=}")
        output += self.biases
        output = self.activation(output)
        return output
