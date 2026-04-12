# layernorm.py
import numpy as np

class LayerNorm:
    def __init__(self, hidden_size, eps=1e-5):
        self.gamma = np.ones(hidden_size)
        self.beta = np.zeros(hidden_size)
        self.eps = eps

    def __call__(self, x):
        # x: [seq_len, hidden_size]
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + self.eps)
        return self.gamma * x_norm + self.beta
