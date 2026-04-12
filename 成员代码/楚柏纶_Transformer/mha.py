# mha.py
import numpy as np
from .layernorm import LayerNorm

class MultiHeadAttention:
    def __init__(self, hidden_size, num_heads):
        assert hidden_size % num_heads == 0
        self.num_heads = num_heads
        self.head_dim = hidden_size // num_heads
        self.Wq = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wk = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wv = np.random.randn(hidden_size, hidden_size) * 0.01
        self.Wo = np.random.randn(hidden_size, hidden_size) * 0.01
        self.ln = LayerNorm(hidden_size)

    def split_heads(self, x):
        # x: [seq_len, hidden_size] -> [seq_len, num_heads, head_dim]
        seq_len = x.shape[0]
        return x.reshape(seq_len, self.num_heads, self.head_dim)

    def merge_heads(self, x):
        # x: [seq_len, num_heads, head_dim] -> [seq_len, hidden_size]
        seq_len = x.shape[0]
        return x.reshape(seq_len, self.num_heads * self.head_dim)

    def softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def __call__(self, x):
        # x: [seq_len, hidden_size]
        x_norm = self.ln(x)
        q = x_norm @ self.Wq
        k = x_norm @ self.Wk
        v = x_norm @ self.Wv
        q = self.split_heads(q)
        k = self.split_heads(k)
        v = self.split_heads(v)
        # Attention: [seq_len, num_heads, seq_len]
        attn_scores = np.einsum('ihd,jhd->ijh', q, k) / np.sqrt(self.head_dim)
        attn_weights = self.softmax(attn_scores)
        attn_output = np.einsum('ijh,jhd->ihd', attn_weights, v)
        out = self.merge_heads(attn_output)
        out = out @ self.Wo
        return out
