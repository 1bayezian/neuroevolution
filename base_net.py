import torch
from torch import nn
from collections import OrderedDict


class BaseNet(nn.Module):

  def encode(self):
    encoded = list()
    weights = self.parameters()

    for param in weights:
      for weight in param.view(-1).detach().numpy():
        encoded.append(weight)
  
    return encoded

  def decode(self, flattened_parameters: list):
    offset = 0

    with torch.no_grad():
      updated = OrderedDict()

      for name, weights in self.named_parameters():
        encoded = flattened_parameters[offset: offset + weights.numel()]
        decoded = torch.FloatTensor(encoded)

        updated[name] = torch.reshape(decoded, weights.shape)
        offset += len(encoded)

      self.load_state_dict(updated)

    return self
