import torch
import torch.nn as nn


class SimpleDQN(nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()

        self.layer_1 = nn.Linear(in_channels, hidden_channels)
        self.layer_2 = nn.Linear(hidden_channels, out_channels)

    def forward(self, x):
        x = nn.functional.relu(self.layer_1(x))
        return self.layer_2(x)