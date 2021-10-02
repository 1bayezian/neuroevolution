import torch
import math
from collections import OrderedDict
from evoman.controller import Controller
from base_net import BaseNet


class PlayerController(Controller):

    def __init__(self, neural_net: BaseNet):
        super(PlayerController, self).__init__()
        self.neural_net = neural_net
        self.fitness = -math.inf
 
    def set_neural_net(self, neural_net: BaseNet) -> None:
        self.neural_net = neural_net

    def control(self, inputs, controller = None):
        # normalize the input
        inputs = (inputs - min(inputs)) / (max(inputs) - min(inputs))
        input_tensor = torch.from_numpy(inputs).float()
        output = self.neural_net(input_tensor)

        # convert to one-hot encoded vector
        max_idx = torch.argmax(output, 0, keepdim = True)
        one_hot = torch.FloatTensor(output.shape)
        one_hot.zero_()
        one_hot.scatter_(0, max_idx, 1)

        return one_hot.detach().numpy()

    def encode(self) -> list:
        return self.neural_net.encode()

    def decode(self, flattened_parameters: list) -> None:
        self.neural_net.decode(flattened_parameters)

        return self
