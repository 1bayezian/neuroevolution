import torch.nn as nn
import torch.nn.functional as F
from base_net import BaseNet


class DeepNet(BaseNet):

  def __init__(self, n_sensors, n_hidden, n_actions):
    super(DeepNet, self).__init__()
    self.n_sensors = n_sensors
    self.n_hidden = n_hidden
    self.n_actions = n_actions

    self.fc1 = nn.Linear(n_sensors, n_hidden)
    self.fc2 = nn.Linear(n_hidden, n_actions)

    nn.init.normal_(self.fc1.weight, mean = 0, std = 1.0)
    nn.init.normal_(self.fc2.weight, mean = 0, std = 1.0)

  def forward(self, x):
    x = self.fc1(x)
    x = F.relu(x)
    x = self.fc2(x)

    return F.softmax(x, dim = -1)

