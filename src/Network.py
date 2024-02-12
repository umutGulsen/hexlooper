from Layer import Layer


class Network:

    def __init__(self, layer_sizes, input_dim, activator):
        self.layers = []

        for layer_size in layer_sizes:
            self.layers.append(Layer(input_dim, layer_size, activation_method=activator))
            input_dim = layer_size

    def randomly_initialize_params(self, network_update_variance):
        for layer in self.layers:
            layer.randomize_params(network_update_variance)

    def forward_prop(self, x):
        for i, layer in enumerate(self.layers):
            x = layer.forward_prop(x)
        return x
