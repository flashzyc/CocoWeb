# ffn.py
import numpy as np
from .layernorm import LayerNorm

class FeedForward:
    def __init__(self, hidden_size, dropout=0.1):
        self.ln = LayerNorm(hidden_size)
        self.w1 = np.random.randn(hidden_size, hidden_size * 4) * 0.01
        self.w2 = np.random.randn(hidden_size * 4, hidden_size) * 0.01
        self.dropout = dropout

    def relu(self, x):
        return np.maximum(0, x)

    def __call__(self, x):
        x_norm = self.ln(x)
        x = self.relu(x_norm @ self.w1)
        # Dropout (inference: scale only)
        x = x * (1 - self.dropout)
        x = x @ self.w2
        return x
